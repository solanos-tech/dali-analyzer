from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

DecodeStatus = Literal["decoded", "reserved", "unknown", "ambiguous"]
FrameSourceV2 = Literal["simulated_log", "serial"]
FrameDirection = Literal["rx_forward16", "rx_forward24", "rx_backward", "tx_backward_local", "unknown"]


class RawFrame(BaseModel):
    ts_ms: int
    direction: FrameDirection
    bit_length: int
    raw_hex: str
    source: FrameSourceV2
    log_name: str | None = None


class DecodedFrame(BaseModel):
    frame_class: str
    name: str
    status: DecodeStatus
    addressing: str | None = None
    opcode: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class TransactionInfo(BaseModel):
    correlation_id: str | None = None
    expects_backward: bool = False
    backward_raw_hex: str | None = None
    latency_ms: int | None = None


class DecodedFrameRecord(BaseModel):
    raw: RawFrame
    decoded: DecodedFrame
    transaction: TransactionInfo


class DecoderRuleError(BaseModel):
    location: str
    message: str


class LogFileInfo(BaseModel):
    name: str
    path: str
    size_bytes: int


class ParsedSnifferFrame(BaseModel):
    ts_ms: int
    direction: str
    raw_hex: str


class SerialPortInfo(BaseModel):
    name: str
    description: str | None = None


class SerialConnectionStatus(BaseModel):
    connected: bool
    port: str | None = None
    baudrate: int | None = None
    message: str | None = None
