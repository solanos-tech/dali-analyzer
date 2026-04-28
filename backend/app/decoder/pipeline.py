from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import AsyncIterator

from .engine import DaliDecoder, DecoderContext
from .models import DecodedFrameRecord, InstanceContextSnapshot, InstanceRuntimeContext, RawFrame, TransactionInfo


@dataclass(slots=True)
class PendingRequest:
    correlation_id: str
    ts_ms: int
    record_index: int


@dataclass(slots=True)
class CorrelationState:
    next_id: itertools.count = field(default_factory=lambda: itertools.count(1))
    pending: list[PendingRequest] = field(default_factory=list)


class DecodePipeline:
    def __init__(self, decoder: DaliDecoder) -> None:
        self.decoder = decoder
        self._context = DecoderContext()

    def decode_snapshot(self, raw_frames: list[RawFrame]) -> list[DecodedFrameRecord]:
        correlation = CorrelationState()
        records: list[DecodedFrameRecord] = []

        for raw in raw_frames:
            decoded = self.decoder.decode(raw, self._context)
            transaction = self._build_transaction(raw, decoded.expects_backward, correlation, len(records))
            records.append(
                DecodedFrameRecord(
                    raw=raw,
                    decoded=decoded.decoded,
                    transaction=transaction,
                )
            )
            self._try_match_backward(records, correlation)
            self._refresh_semantic_level(records[-1])

        return records

    async def decode_stream(self, raw_stream: AsyncIterator[RawFrame]) -> AsyncIterator[DecodedFrameRecord]:
        correlation = CorrelationState()
        records: list[DecodedFrameRecord] = []

        async for raw in raw_stream:
            decoded = self.decoder.decode(raw, self._context)
            transaction = self._build_transaction(raw, decoded.expects_backward, correlation, len(records))
            record = DecodedFrameRecord(raw=raw, decoded=decoded.decoded, transaction=transaction)
            records.append(record)
            self._try_match_backward(records, correlation)
            self._refresh_semantic_level(records[-1])
            yield records[-1]

    def instance_context_snapshot(self) -> InstanceContextSnapshot:
        devices: list[InstanceRuntimeContext] = []
        for short_address, instances in self._context.instances.items():
            for instance, state in instances.items():
                devices.append(
                    InstanceRuntimeContext(
                        short_address=short_address,
                        instance=instance,
                        instance_type=state.instance_type,
                        event_scheme=state.event_scheme,
                        event_filter=state.event_filter,
                        event_priority=state.event_priority,
                    )
                )
        devices.sort(key=lambda item: (item.short_address, item.instance))
        return InstanceContextSnapshot(devices=devices)

    def _build_transaction(
        self,
        raw: RawFrame,
        expects_backward: bool,
        correlation: CorrelationState,
        record_index: int,
    ) -> TransactionInfo:
        if raw.direction in {"rx_backward", "tx_backward_local"}:
            return TransactionInfo(expects_backward=False)

        if not expects_backward:
            return TransactionInfo(expects_backward=False)

        correlation_id = f"tx-{next(correlation.next_id)}"
        correlation.pending.append(
            PendingRequest(
                correlation_id=correlation_id,
                ts_ms=raw.ts_ms,
                record_index=record_index,
            )
        )
        return TransactionInfo(correlation_id=correlation_id, expects_backward=True)

    def _try_match_backward(self, records: list[DecodedFrameRecord], correlation: CorrelationState) -> None:
        if not records:
            return

        last = records[-1]
        if last.raw.direction not in {"rx_backward", "tx_backward_local"}:
            return

        if not correlation.pending:
            return

        pending = correlation.pending.pop(0)
        forward = records[pending.record_index]
        latency_ms = max(last.raw.ts_ms - pending.ts_ms, 0)

        forward.transaction.backward_raw_hex = last.raw.raw_hex
        forward.transaction.latency_ms = latency_ms
        last.transaction.correlation_id = pending.correlation_id
        last.transaction.backward_raw_hex = last.raw.raw_hex
        last.transaction.latency_ms = latency_ms
        self._apply_context_from_backward(forward, last)

    def _apply_context_from_backward(self, forward: DecodedFrameRecord, backward: DecodedFrameRecord) -> None:
        params = forward.decoded.params
        query_name = params.get("semantic_query")
        if not isinstance(query_name, str):
            return

        short_address = params.get("source_short_address")
        instance = params.get("instance")
        if not isinstance(short_address, int) or not isinstance(instance, int):
            return

        state = self._context.ensure_instance(short_address, instance)
        raw_hex = backward.raw.raw_hex
        try:
            value = int(raw_hex, 16) & 0xFF
        except ValueError:
            return

        if query_name == "query_instance_type":
            state.instance_type = value
            return
        if query_name == "query_event_scheme":
            state.event_scheme = value
            return
        if query_name.startswith("query_event_filter"):
            state.event_filter = value
            return
        if query_name == "query_event_priority":
            state.event_priority = value

    def _refresh_semantic_level(self, record: DecodedFrameRecord) -> None:
        if record.decoded.frame_class != "forward24_input_notification":
            return
        params = record.decoded.params
        short_address = params.get("source_short_address")
        instance = params.get("instance")
        if not isinstance(short_address, int) or not isinstance(instance, int):
            return

        state = self._context.ensure_instance(short_address, instance)
        if state.instance_type is None:
            record.decoded.semantic_level = "generic"
            record.decoded.semantic_reason = "missing_instance_type"
            record.decoded.semantic_name = "input_notification"
            return

        params["instance_type"] = f"0x{state.instance_type:02X}"
        record.decoded.semantic_level = "instance_aware"
        record.decoded.semantic_reason = "missing_event_scheme"
        record.decoded.semantic_name = "instance_type_known"

        if state.event_scheme is None:
            return

        params["event_scheme"] = f"0x{state.event_scheme:02X}"
        record.decoded.semantic_level = "full"
        record.decoded.semantic_reason = None
        record.decoded.semantic_name = "instance_event_semantic"
