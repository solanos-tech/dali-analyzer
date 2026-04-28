from __future__ import annotations

import asyncio
import os
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, cast

from .models import FrameDirection, FrameSourceV2, ParsedSnifferFrame, RawFrame

SNIFFER_LINE_RE = re.compile(r"ts_ms=(?P<ts>\d+)\s+dir=(?P<dir>[a-zA-Z0-9_]+)\s+raw=(?P<raw>0x[0-9A-Fa-f]+)")


@dataclass(slots=True)
class RuntimeSourceConfig:
    simulated_logs_dir: Path
    serial_port: str | None
    serial_baudrate: int


class SourceError(RuntimeError):
    pass


class SourceRegistry:
    def __init__(self, config: RuntimeSourceConfig) -> None:
        self.config = config
        self._sim_cache: dict[str, list[ParsedSnifferFrame]] = {}

    def list_simulated_logs(self) -> list[Path]:
        if not self.config.simulated_logs_dir.exists():
            return []
        return sorted(self.config.simulated_logs_dir.glob("*.log"))

    def load_simulated_log(self, log_name: str) -> list[ParsedSnifferFrame]:
        if log_name in self._sim_cache:
            return self._sim_cache[log_name]

        candidate = self.config.simulated_logs_dir / log_name
        if not candidate.exists():
            raise SourceError(f"Log file not found: {log_name}")

        frames: list[ParsedSnifferFrame] = []
        for line in candidate.read_text(encoding="utf-8", errors="ignore").splitlines():
            match = SNIFFER_LINE_RE.search(line)
            if not match:
                continue

            frames.append(
                ParsedSnifferFrame(
                    ts_ms=int(match.group("ts")),
                    direction=match.group("dir"),
                    raw_hex=match.group("raw").upper(),
                )
            )

        if not frames:
            raise SourceError(f"No parseable sniffer frames found in {log_name}")

        self._sim_cache[log_name] = frames
        return frames

    async def stream_simulated_log(self, log_name: str) -> AsyncIterator[RawFrame]:
        frames = self.load_simulated_log(log_name)
        while True:
            prev_ts: int | None = None
            for frame in frames:
                if prev_ts is not None:
                    gap_ms = max(frame.ts_ms - prev_ts, 0)
                    await asyncio.sleep(gap_ms / 1000)
                prev_ts = frame.ts_ms
                yield to_raw_frame(frame, source="simulated_log", log_name=log_name)

    def snapshot_simulated_log(self, log_name: str, limit: int) -> list[RawFrame]:
        frames = self.load_simulated_log(log_name)
        return [to_raw_frame(frame, source="simulated_log", log_name=log_name) for frame in frames[:limit]]

    async def stream_serial(self) -> AsyncIterator[RawFrame]:
        reader = SerialSourceReader(port=self.config.serial_port, baudrate=self.config.serial_baudrate)
        async for frame in reader.stream():
            yield frame

    def snapshot_serial(self, limit: int) -> list[RawFrame]:
        reader = SerialSourceReader(port=self.config.serial_port, baudrate=self.config.serial_baudrate)
        return reader.snapshot(limit)


class SerialSourceReader:
    """Serial adapter prepared for real hardware with a safe fallback for local development."""

    def __init__(self, port: str | None, baudrate: int) -> None:
        self.port = port
        self.baudrate = baudrate
        self._fallback_frames = [
            ParsedSnifferFrame(ts_ms=0, direction="rx_forward16", raw_hex="0xFF91"),
            ParsedSnifferFrame(ts_ms=30, direction="rx_backward", raw_hex="0xFF"),
            ParsedSnifferFrame(ts_ms=80, direction="rx_forward24", raw_hex="0x01FE30"),
            ParsedSnifferFrame(ts_ms=95, direction="rx_backward", raw_hex="0x22"),
            ParsedSnifferFrame(ts_ms=140, direction="rx_forward24", raw_hex="0x01FE3C"),
            ParsedSnifferFrame(ts_ms=155, direction="rx_backward", raw_hex="0x4C"),
        ]

    async def stream(self) -> AsyncIterator[RawFrame]:
        if self.port:
            serial_frames = await self._try_stream_from_serial()
            if serial_frames is not None:
                async for frame in serial_frames:
                    yield frame
                return

        while True:
            prev_ts: int | None = None
            for fallback_frame in self._fallback_frames:
                if prev_ts is not None:
                    await asyncio.sleep(max(fallback_frame.ts_ms - prev_ts, 0) / 1000)
                prev_ts = fallback_frame.ts_ms
                yield to_raw_frame(fallback_frame, source="serial", log_name=None)

    def snapshot(self, limit: int) -> list[RawFrame]:
        if limit <= 0:
            return []

        frames: list[RawFrame] = []
        ts = 0
        for _ in range(limit):
            base = random.choice(self._fallback_frames)
            ts += random.randint(20, 120)
            frames.append(
                RawFrame(
                    ts_ms=ts,
                    direction=_safe_direction(base.direction),
                    bit_length=_bit_length_for_direction(base.direction),
                    raw_hex=base.raw_hex,
                    source="serial",
                    log_name=None,
                )
            )
        return frames

    async def _try_stream_from_serial(self) -> AsyncIterator[RawFrame] | None:
        try:
            import serial  # type: ignore[import-untyped]
        except Exception:
            return None

        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=1)
        except Exception:
            return None

        async def _iterator() -> AsyncIterator[RawFrame]:
            loop = asyncio.get_running_loop()
            while True:
                raw_line = await loop.run_in_executor(None, ser.readline)
                line = raw_line.decode("utf-8", errors="ignore")
                match = SNIFFER_LINE_RE.search(line)
                if not match:
                    continue
                yield RawFrame(
                    ts_ms=int(match.group("ts")),
                    direction=_safe_direction(match.group("dir")),
                    bit_length=_bit_length_for_direction(match.group("dir")),
                    raw_hex=match.group("raw").upper(),
                    source="serial",
                    log_name=None,
                )

        return _iterator()


def build_source_registry() -> SourceRegistry:
    sim_dir = _resolve_simulated_logs_dir()
    serial_port = os.getenv("SERIAL_PORT")
    serial_baudrate = int(os.getenv("SERIAL_BAUDRATE", "115200"))

    return SourceRegistry(
        RuntimeSourceConfig(
            simulated_logs_dir=sim_dir,
            serial_port=serial_port,
            serial_baudrate=serial_baudrate,
        )
    )


def _resolve_simulated_logs_dir() -> Path:
    configured = os.getenv("SIM_LOG_DIR")
    if configured:
        return Path(configured)

    cwd = Path.cwd()
    source_file = Path(__file__).resolve()
    candidates = [
        cwd / "docs" / "standards",
        cwd.parent / "docs" / "standards",
        source_file.parents[3] / "docs" / "standards",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


def to_raw_frame(frame: ParsedSnifferFrame, source: FrameSourceV2, log_name: str | None) -> RawFrame:
    return RawFrame(
        ts_ms=frame.ts_ms,
        direction=_safe_direction(frame.direction),
        bit_length=_bit_length_for_direction(frame.direction),
        raw_hex=frame.raw_hex,
        source=source,
        log_name=log_name,
    )


def _safe_direction(value: str) -> FrameDirection:
    known = {"rx_forward16", "rx_forward24", "rx_backward", "tx_backward_local"}
    return cast(FrameDirection, value if value in known else "unknown")


def _bit_length_for_direction(direction: str) -> int:
    if direction == "rx_forward16":
        return 16
    if direction == "rx_forward24":
        return 24
    if direction in {"rx_backward", "tx_backward_local"}:
        return 8
    return 0
