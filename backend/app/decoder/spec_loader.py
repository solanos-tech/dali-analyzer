from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import DecoderRuleError


@dataclass(slots=True)
class DecoderSpec:
    raw: dict[str, Any]
    path: Path


class SpecValidationError(RuntimeError):
    def __init__(self, errors: list[DecoderRuleError]) -> None:
        self.errors = errors
        message = "Decoder spec validation failed:\n" + "\n".join(
            f"- {error.location}: {error.message}" for error in errors
        )
        super().__init__(message)


REQUIRED_TOP_LEVEL = {"version", "frame_types", "forward16", "forward24", "correlation"}
REQUIRED_FORWARD16 = {"special_commands", "opcode_table"}
REQUIRED_FORWARD24 = {"special_c1", "device_level_opcode_table"}
REQUIRED_CORRELATION = {"backward_directions"}
ALLOWED_STATUS = {"decoded", "reserved", "unknown", "ambiguous"}


def load_decoder_spec(spec_path: Path, schema_path: Path) -> DecoderSpec:
    raw_spec = json.loads(spec_path.read_text(encoding="utf-8"))
    raw_schema = json.loads(schema_path.read_text(encoding="utf-8"))

    errors = _validate_against_min_schema(raw_spec, raw_schema)
    errors.extend(_validate_semantics(raw_spec))

    if errors:
        raise SpecValidationError(errors)

    return DecoderSpec(raw=raw_spec, path=spec_path)


def _validate_against_min_schema(spec: dict[str, Any], schema: dict[str, Any]) -> list[DecoderRuleError]:
    errors: list[DecoderRuleError] = []

    if not isinstance(schema, dict):
        errors.append(DecoderRuleError(location="schema", message="Schema file must be a JSON object"))
        return errors

    if not isinstance(spec, dict):
        errors.append(DecoderRuleError(location="spec", message="Spec file must be a JSON object"))
        return errors

    missing = REQUIRED_TOP_LEVEL - set(spec)
    for key in sorted(missing):
        errors.append(DecoderRuleError(location=key, message="Missing required top-level key"))

    if "forward16" in spec and isinstance(spec["forward16"], dict):
        missing_forward16 = REQUIRED_FORWARD16 - set(spec["forward16"])
        for key in sorted(missing_forward16):
            errors.append(DecoderRuleError(location=f"forward16.{key}", message="Missing required key"))
    else:
        errors.append(DecoderRuleError(location="forward16", message="forward16 must be an object"))

    if "forward24" in spec and isinstance(spec["forward24"], dict):
        missing_forward24 = REQUIRED_FORWARD24 - set(spec["forward24"])
        for key in sorted(missing_forward24):
            errors.append(DecoderRuleError(location=f"forward24.{key}", message="Missing required key"))
    else:
        errors.append(DecoderRuleError(location="forward24", message="forward24 must be an object"))

    if "correlation" in spec and isinstance(spec["correlation"], dict):
        missing_corr = REQUIRED_CORRELATION - set(spec["correlation"])
        for key in sorted(missing_corr):
            errors.append(DecoderRuleError(location=f"correlation.{key}", message="Missing required key"))
    else:
        errors.append(DecoderRuleError(location="correlation", message="correlation must be an object"))

    return errors


def _validate_semantics(spec: dict[str, Any]) -> list[DecoderRuleError]:
    errors: list[DecoderRuleError] = []

    _validate_pattern_rules(spec, "forward16.special_commands", errors)
    _validate_pattern_rules(spec, "forward24.special_c1", errors)
    _validate_opcode_table(spec, "forward16.opcode_table", errors)
    _validate_opcode_table(spec, "forward24.device_level_opcode_table", errors)

    backward_directions = spec.get("correlation", {}).get("backward_directions", [])
    if not isinstance(backward_directions, list) or not backward_directions:
        errors.append(
            DecoderRuleError(
                location="correlation.backward_directions",
                message="Must contain at least one backward direction",
            )
        )

    return errors


def _validate_pattern_rules(spec: dict[str, Any], path: str, errors: list[DecoderRuleError]) -> None:
    rules = _get_path(spec, path)
    if not isinstance(rules, list):
        errors.append(DecoderRuleError(location=path, message="Must be an array"))
        return

    seen_exact: set[int] = set()

    for idx, rule in enumerate(rules):
        location = f"{path}[{idx}]"
        if not isinstance(rule, dict):
            errors.append(DecoderRuleError(location=location, message="Rule must be an object"))
            continue

        status = rule.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(DecoderRuleError(location=f"{location}.status", message="Invalid status value"))

        match = rule.get("match")
        if not isinstance(match, dict):
            errors.append(DecoderRuleError(location=f"{location}.match", message="match must be an object"))
            continue

        match_type = match.get("type")
        if match_type == "exact":
            value = _parse_hex(match.get("value"), bits=24)
            if value is None:
                errors.append(
                    DecoderRuleError(location=f"{location}.match.value", message="Invalid exact hex value")
                )
                continue
            if value in seen_exact:
                errors.append(DecoderRuleError(location=location, message="Duplicate exact pattern"))
            seen_exact.add(value)
        elif match_type == "mask":
            mask = _parse_hex(match.get("mask"), bits=24)
            value = _parse_hex(match.get("value"), bits=24)
            if mask is None or value is None:
                errors.append(DecoderRuleError(location=location, message="Invalid mask/value hex"))
            elif value & ~mask:
                errors.append(
                    DecoderRuleError(
                        location=location,
                        message="Mask/value mismatch: value must fit mask",
                    )
                )
        else:
            errors.append(DecoderRuleError(location=f"{location}.match.type", message="Unknown match type"))


def _validate_opcode_table(spec: dict[str, Any], path: str, errors: list[DecoderRuleError]) -> None:
    rules = _get_path(spec, path)
    if not isinstance(rules, list):
        errors.append(DecoderRuleError(location=path, message="Must be an array"))
        return

    covered: list[tuple[int, int, str]] = []

    for idx, rule in enumerate(rules):
        location = f"{path}[{idx}]"
        if not isinstance(rule, dict):
            errors.append(DecoderRuleError(location=location, message="Rule must be an object"))
            continue

        status = rule.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(DecoderRuleError(location=f"{location}.status", message="Invalid status value"))

        opcode = rule.get("opcode")
        if not isinstance(opcode, dict):
            errors.append(DecoderRuleError(location=f"{location}.opcode", message="opcode must be an object"))
            continue

        opcode_type = opcode.get("type")
        if opcode_type == "exact":
            value = _parse_hex(opcode.get("value"), bits=8)
            if value is None:
                errors.append(DecoderRuleError(location=f"{location}.opcode.value", message="Invalid opcode value"))
                continue
            interval = (value, value)
        elif opcode_type == "range":
            start = _parse_hex(opcode.get("start"), bits=8)
            end = _parse_hex(opcode.get("end"), bits=8)
            if start is None or end is None:
                errors.append(DecoderRuleError(location=location, message="Invalid opcode range"))
                continue
            if end < start:
                errors.append(DecoderRuleError(location=location, message="Range end must be >= start"))
                continue
            interval = (start, end)
        else:
            errors.append(DecoderRuleError(location=f"{location}.opcode.type", message="Unknown opcode type"))
            continue

        for existing_start, existing_end, existing_loc in covered:
            if not (interval[1] < existing_start or interval[0] > existing_end):
                errors.append(
                    DecoderRuleError(
                        location=location,
                        message=f"Opcode range overlaps with {existing_loc}",
                    )
                )
                break
        covered.append((interval[0], interval[1], location))


def _parse_hex(value: Any, bits: int) -> int | None:
    if not isinstance(value, str) or not value.startswith("0x"):
        return None
    try:
        parsed = int(value, 16)
    except ValueError:
        return None

    max_value = (1 << bits) - 1
    if parsed < 0 or parsed > max_value:
        return None
    return parsed


def _get_path(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current