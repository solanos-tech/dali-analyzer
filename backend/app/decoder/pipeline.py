from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import AsyncIterator

from .engine import DaliDecoder, DecoderContext
from .models import DecodedFrameRecord, RawFrame, TransactionInfo


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

    def decode_snapshot(self, raw_frames: list[RawFrame]) -> list[DecodedFrameRecord]:
        context = DecoderContext()
        correlation = CorrelationState()
        records: list[DecodedFrameRecord] = []

        for raw in raw_frames:
            decoded = self.decoder.decode(raw, context)
            transaction = self._build_transaction(raw, decoded.expects_backward, correlation, len(records))
            records.append(
                DecodedFrameRecord(
                    raw=raw,
                    decoded=decoded.decoded,
                    transaction=transaction,
                )
            )
            self._try_match_backward(records, correlation)

        return records

    async def decode_stream(self, raw_stream: AsyncIterator[RawFrame]) -> AsyncIterator[DecodedFrameRecord]:
        context = DecoderContext()
        correlation = CorrelationState()
        records: list[DecodedFrameRecord] = []

        async for raw in raw_stream:
            decoded = self.decoder.decode(raw, context)
            transaction = self._build_transaction(raw, decoded.expects_backward, correlation, len(records))
            record = DecodedFrameRecord(raw=raw, decoded=decoded.decoded, transaction=transaction)
            records.append(record)
            self._try_match_backward(records, correlation)
            yield records[-1]

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