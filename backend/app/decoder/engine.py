from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import DecodeStatus, DecodedFrame, RawFrame, SemanticLevel
from .spec_loader import DecoderSpec


INSTANCE_TYPE_NAMES: dict[int, str] = {
    0x00: "generic_sensor",
    0x01: "push_button",
    0x02: "absolute_input",
    0x03: "occupancy_sensor",
    0x04: "light_sensor",
    0x05: "colour_sensor",
    0x06: "general_purpose_sensor",
    0x07: "thermal_sensor",
}

INSTANCE_EVENT_SEMANTICS: dict[int, dict[int, str]] = {
    0x00: {
        0x8C: "input_value_notification",
        0x8D: "input_value_latch_notification",
    },
    0x03: {
        0x8C: "occupancy_event_active",
        0x8D: "occupancy_event_cleared",
    },
    0x04: {
        0x8C: "light_level_changed",
        0x8D: "light_level_latched",
    },
}

INSTANCE_QUERY_OPCODE_MAP: dict[int, str] = {
    0x80: "query_instance_type",
    0x84: "query_event_priority",
    0x8B: "query_event_scheme",
    0x90: "query_event_filter_0_7",
    0x91: "query_event_filter_8_15",
    0x92: "query_event_filter_16_23",
}


@dataclass(slots=True)
class InstanceState:
    instance_type: int | None = None
    event_scheme: int | None = None
    event_filter: int | None = None
    event_priority: int | None = None


@dataclass(slots=True)
class DecoderContext:
    dtr0: int | None = None
    dtr1: int | None = None
    dtr2: int | None = None
    instances: dict[int, dict[int, InstanceState]] = field(default_factory=dict)

    def ensure_instance(self, short_address: int, instance: int) -> InstanceState:
        device = self.instances.setdefault(short_address, {})
        return device.setdefault(instance, InstanceState())


@dataclass(slots=True)
class DecodedEnvelope:
    decoded: DecodedFrame
    expects_backward: bool


@dataclass(slots=True)
class OpcodeRule:
    start: int
    end: int
    name: str
    status: DecodeStatus
    expects_backward: bool
    send_twice: bool


@dataclass(slots=True)
class PatternRule:
    match_type: str
    value: int
    mask: int
    name: str
    status: DecodeStatus
    expects_backward: bool
    send_twice: bool


@dataclass(slots=True)
class CompiledSpec:
    forward16_special: list[PatternRule] = field(default_factory=list)
    forward16_opcode: list[OpcodeRule] = field(default_factory=list)
    forward24_special: list[PatternRule] = field(default_factory=list)
    forward24_device_opcode: list[OpcodeRule] = field(default_factory=list)
    backward_directions: set[str] = field(default_factory=set)


class DaliDecoder:
    def __init__(self, spec: DecoderSpec) -> None:
        self.spec = _compile_spec(spec.raw)

    def decode(self, raw: RawFrame, context: DecoderContext) -> DecodedEnvelope:
        if raw.direction in self.spec.backward_directions:
            return DecodedEnvelope(
                decoded=DecodedFrame(
                    frame_class="backward",
                    name="BACKWARD FRAME",
                    status="decoded",
                    addressing=None,
                    opcode=None,
                    params={"raw_value": raw.raw_hex},
                    confidence=1.0,
                ),
                expects_backward=False,
            )

        if raw.direction == "rx_forward16":
            return self._decode_forward16(raw, context)

        if raw.direction == "rx_forward24":
            return self._decode_forward24(raw, context)

        return DecodedEnvelope(
            decoded=DecodedFrame(
                frame_class="unknown",
                name="UNKNOWN FRAME DIRECTION",
                status="unknown",
                params={"direction": raw.direction},
                warnings=["Unsupported frame direction"],
                confidence=0.0,
            ),
            expects_backward=False,
        )

    def _decode_forward16(self, raw: RawFrame, context: DecoderContext) -> DecodedEnvelope:
        value = int(raw.raw_hex, 16)

        for special_rule in self.spec.forward16_special:
            if _pattern_match(value, special_rule):
                special_params: dict[str, Any] = {"value": raw.raw_hex}
                lower_byte = value & 0xFF
                if special_rule.match_type == "mask":
                    special_params["param"] = f"0x{lower_byte:02X}"
                if special_rule.name == "SET DTR0":
                    context.dtr0 = lower_byte
                return DecodedEnvelope(
                    decoded=DecodedFrame(
                        frame_class="forward16_special",
                        name=special_rule.name,
                        status=special_rule.status,
                        params=special_params,
                        confidence=1.0 if special_rule.status == "decoded" else 0.7,
                    ),
                    expects_backward=special_rule.expects_backward,
                )

        byte0 = (value >> 8) & 0xFF
        byte1 = value & 0xFF
        s_bit = byte0 & 0x01

        if s_bit == 0:
            addressing, raw_params = _decode_forward16_addressing(byte0)
            dapc_params: dict[str, Any] = dict(raw_params)
            dapc_params["level"] = f"0x{byte1:02X}"
            name = "DIRECT ARC POWER CONTROL"
            return DecodedEnvelope(
                decoded=DecodedFrame(
                    frame_class="forward16_dapc",
                    name=name,
                    status="decoded",
                    addressing=addressing,
                    opcode=f"0x{byte1:02X}",
                    params=dapc_params,
                    confidence=1.0,
                ),
                expects_backward=False,
            )

        addressing, raw_params = _decode_forward16_addressing(byte0)
        cmd_params: dict[str, Any] = dict(raw_params)
        opcode_rule = _find_opcode_rule(self.spec.forward16_opcode, byte1)
        if opcode_rule is None:
            decoded = DecodedFrame(
                frame_class="forward16_command",
                name="UNKNOWN OPCODE",
                status="unknown",
                addressing=addressing,
                opcode=f"0x{byte1:02X}",
                params=cmd_params,
                warnings=["Opcode not present in decoder spec"],
                confidence=0.0,
            )
            return DecodedEnvelope(decoded=decoded, expects_backward=False)

        frame_class = "forward16_query" if opcode_rule.expects_backward else "forward16_command"
        if opcode_rule.start == 0x10 and opcode_rule.end == 0x1F:
            cmd_params["scene"] = byte1 & 0x0F
        elif opcode_rule.start == 0x30 and opcode_rule.end == 0x3F:
            cmd_params["scene"] = byte1 & 0x0F
        elif opcode_rule.start in (0x40, 0x50, 0x60) and opcode_rule.end in (0x4F, 0x5F, 0x6F):
            cmd_params["group_or_scene"] = byte1 & 0x0F

        decoded = DecodedFrame(
            frame_class=frame_class,
            name=opcode_rule.name,
            status=opcode_rule.status,
            addressing=addressing,
            opcode=f"0x{byte1:02X}",
            params=cmd_params,
            warnings=["Send twice recommended"] if opcode_rule.send_twice else [],
            confidence=1.0 if opcode_rule.status == "decoded" else 0.6,
        )
        return DecodedEnvelope(decoded=decoded, expects_backward=opcode_rule.expects_backward)

    def _decode_forward24(self, raw: RawFrame, context: DecoderContext) -> DecodedEnvelope:
        value = int(raw.raw_hex, 16)

        for special_rule in self.spec.forward24_special:
            if _pattern_match(value, special_rule):
                lower_byte = value & 0xFF
                if special_rule.name == "SET DTR0":
                    context.dtr0 = lower_byte
                elif special_rule.name == "SET DTR1":
                    context.dtr1 = lower_byte
                elif special_rule.name == "SET DTR2":
                    context.dtr2 = lower_byte

                params = {"value": raw.raw_hex}
                if special_rule.match_type == "mask":
                    params["param"] = f"0x{lower_byte:02X}"

                decoded = DecodedFrame(
                    frame_class="forward24_special",
                    name=special_rule.name,
                    status=special_rule.status,
                    params=params,
                    warnings=["Send twice recommended"] if special_rule.send_twice else [],
                    confidence=1.0 if special_rule.status == "decoded" else 0.7,
                )
                return DecodedEnvelope(decoded=decoded, expects_backward=special_rule.expects_backward)

        b0 = (value >> 16) & 0xFF
        b1 = (value >> 8) & 0xFF
        b2 = value & 0xFF

        if 0xC0 <= b0 <= 0xCF and b0 != 0xC1:
            decoded = DecodedFrame(
                frame_class="forward24_special_or_helper",
                name="SPECIAL / HELPER FRAME",
                status="decoded_generic",
                addressing=f"raw:0x{b0:02X}",
                opcode=f"0x{b2:02X}",
                params={
                    "byte0": f"0x{b0:02X}",
                    "byte1": f"0x{b1:02X}",
                    "byte2": f"0x{b2:02X}",
                },
                warnings=["Special/helper 24-bit range requires dedicated command mapping"],
                confidence=0.8,
                semantic_level="generic",
                semantic_reason="special_helper_range",
            )
            return DecodedEnvelope(decoded=decoded, expects_backward=False)

        if b1 == 0xFE:
            opcode_rule = _find_opcode_rule(self.spec.forward24_device_opcode, b2)
            if opcode_rule is None:
                decoded = DecodedFrame(
                    frame_class="forward24_device_level",
                    name="UNKNOWN DEVICE-LEVEL OPCODE",
                    status="unknown",
                    addressing=_decode_control_device_address(b0),
                    opcode=f"0x{b2:02X}",
                    params={},
                    warnings=["Opcode not present in decoder spec"],
                    confidence=0.0,
                    semantic_level="generic",
                    semantic_reason="unknown_device_level_opcode",
                )
                return DecodedEnvelope(decoded=decoded, expects_backward=False)

            decoded = DecodedFrame(
                frame_class="forward24_device_level_query"
                if opcode_rule.expects_backward
                else "forward24_device_level_instruction",
                name=opcode_rule.name,
                status=opcode_rule.status,
                addressing=_decode_control_device_address(b0),
                opcode=f"0x{b2:02X}",
                params={
                    "instance_or_device_opcode": f"0x{b2:02X}",
                    "dtr0": context.dtr0,
                    "dtr1": context.dtr1,
                    "dtr2": context.dtr2,
                },
                warnings=["Send twice recommended"] if opcode_rule.send_twice else [],
                confidence=1.0 if opcode_rule.status == "decoded" else 0.65,
                semantic_level="generic",
            )
            return DecodedEnvelope(decoded=decoded, expects_backward=opcode_rule.expects_backward)

        if (b0 & 0x01) == 0x01 and b0 <= 0x7F:
            short_address = b0 >> 1
            instance = b1
            semantic_query = INSTANCE_QUERY_OPCODE_MAP.get(b2)
            if semantic_query is not None:
                decoded = DecodedFrame(
                    frame_class="forward24_instance_command_or_query",
                    name="INSTANCE QUERY",
                    status="decoded_generic",
                    addressing=f"short:{short_address}",
                    opcode=f"0x{b2:02X}",
                    params={
                        "source_short_address": short_address,
                        "instance": instance,
                        "instance_opcode": f"0x{b2:02X}",
                        "semantic_query": semantic_query,
                    },
                    warnings=[],
                    confidence=0.8,
                    semantic_level="generic",
                    semantic_reason="instance_query_requires_backward",
                )
                return DecodedEnvelope(decoded=decoded, expects_backward=True)

            instance_state = context.ensure_instance(short_address, instance)
            semantic_level: SemanticLevel = "generic"
            semantic_reason: str | None = "missing_instance_type"
            semantic_name = "input_notification"
            status: DecodeStatus = "decoded_generic"
            confidence = 0.8

            if instance_state.instance_type is not None:
                semantic_level = "instance_aware"
                semantic_reason = "missing_event_scheme"
                semantic_name = INSTANCE_TYPE_NAMES.get(instance_state.instance_type, "instance_type_known")
                if instance_state.event_scheme is not None:
                    semantic_level = "full"
                    semantic_reason = None
                    semantic_name = INSTANCE_EVENT_SEMANTICS.get(instance_state.instance_type, {}).get(
                        b2, "instance_event_unmapped"
                    )

            decoded = DecodedFrame(
                frame_class="forward24_input_notification",
                name="INPUT NOTIFICATION",
                status=status,
                addressing=f"short:{short_address}",
                opcode=f"0x{b2:02X}",
                params={
                    "source_short_address": short_address,
                    "instance": instance,
                    "event_info": f"0x{b2:02X}",
                    "instance_type": (
                        f"0x{instance_state.instance_type:02X}"
                        if instance_state.instance_type is not None
                        else None
                    ),
                    "event_scheme": (
                        f"0x{instance_state.event_scheme:02X}"
                        if instance_state.event_scheme is not None
                        else None
                    ),
                    "event_filter": (
                        f"0x{instance_state.event_filter:02X}"
                        if instance_state.event_filter is not None
                        else None
                    ),
                    "event_priority": (
                        f"0x{instance_state.event_priority:02X}"
                        if instance_state.event_priority is not None
                        else None
                    ),
                    "backward_expected": False,
                },
                warnings=[],
                confidence=confidence,
                semantic_level=semantic_level,
                semantic_name=semantic_name,
                semantic_reason=semantic_reason,
            )
            return DecodedEnvelope(decoded=decoded, expects_backward=False)

        decoded = DecodedFrame(
            frame_class="forward24_instance_command_or_query",
            name="INSTANCE COMMAND / QUERY",
            status="ambiguous",
            addressing=_decode_control_device_address(b0),
            opcode=f"0x{b2:02X}",
            params={
                "instance": b1,
                "payload": f"0x{b2:02X}",
            },
            warnings=["Needs instance type + sender context for exact interpretation"],
            confidence=0.45,
            semantic_level="generic",
            semantic_reason="ambiguous_instance_or_query",
        )
        return DecodedEnvelope(decoded=decoded, expects_backward=False)


def _compile_spec(raw: dict[str, Any]) -> CompiledSpec:
    return CompiledSpec(
        forward16_special=[_compile_pattern_rule(rule) for rule in raw["forward16"]["special_commands"]],
        forward16_opcode=[_compile_opcode_rule(rule) for rule in raw["forward16"]["opcode_table"]],
        forward24_special=[_compile_pattern_rule(rule) for rule in raw["forward24"]["special_c1"]],
        forward24_device_opcode=[
            _compile_opcode_rule(rule) for rule in raw["forward24"]["device_level_opcode_table"]
        ],
        backward_directions=set(raw["correlation"]["backward_directions"]),
    )


def _compile_pattern_rule(rule: dict[str, Any]) -> PatternRule:
    match = rule["match"]
    if match["type"] == "exact":
        value = int(match["value"], 16)
        mask = (1 << 24) - 1
    else:
        value = int(match["value"], 16)
        mask = int(match["mask"], 16)

    return PatternRule(
        match_type=match["type"],
        value=value,
        mask=mask,
        name=rule["name"],
        status=rule["status"],
        expects_backward=bool(rule.get("expects_backward", False)),
        send_twice=bool(rule.get("send_twice", False)),
    )


def _compile_opcode_rule(rule: dict[str, Any]) -> OpcodeRule:
    opcode = rule["opcode"]
    if opcode["type"] == "exact":
        start = end = int(opcode["value"], 16)
    else:
        start = int(opcode["start"], 16)
        end = int(opcode["end"], 16)

    return OpcodeRule(
        start=start,
        end=end,
        name=rule["name"],
        status=rule["status"],
        expects_backward=bool(rule.get("expects_backward", False)),
        send_twice=bool(rule.get("send_twice", False)),
    )


def _pattern_match(value: int, rule: PatternRule) -> bool:
    if rule.match_type == "exact":
        return value == rule.value
    return (value & rule.mask) == rule.value


def _find_opcode_rule(rules: list[OpcodeRule], opcode: int) -> OpcodeRule | None:
    for rule in rules:
        if rule.start <= opcode <= rule.end:
            return rule
    return None


def _decode_forward16_addressing(byte0: int) -> tuple[str, dict[str, Any]]:
    if byte0 == 0xFE:
        return "broadcast_dapc", {"broadcast": True}
    if byte0 == 0xFF:
        return "broadcast_command", {"broadcast": True}
    if byte0 < 0x80:
        return "short_address", {"short_address": byte0 >> 1}
    if 0x80 <= byte0 <= 0x9F:
        return "group_address", {"group": (byte0 - 0x80) >> 1}
    return "special_or_extended", {"byte0": f"0x{byte0:02X}"}


def _decode_control_device_address(byte0: int) -> str:
    if byte0 == 0xFF:
        return "broadcast"
    if byte0 <= 0x7F:
        return f"short:{byte0 >> 1}"
    if 0x80 <= byte0 <= 0x9F:
        return f"group:{(byte0 - 0x80) >> 1}"
    return f"raw:0x{byte0:02X}"
