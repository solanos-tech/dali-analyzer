from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import AsyncIterator, Literal

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.decoder import (
    DaliDecoder,
    DecodePipeline,
    SourceError,
    build_source_registry,
    load_decoder_spec,
)
from app.decoder.models import DecodedFrameRecord, LogFileInfo


class Frame(BaseModel):
    timestamp: str
    address: str
    command: str
    source: Literal["mock", "serial"]


app = FastAPI(title="DALI Analyzer API")

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _spec_paths() -> tuple[Path, Path]:
    root = Path(__file__).resolve().parent
    return root / "specs" / "dali_decoder.json", root / "specs" / "dali_decoder.schema.json"


def _build_runtime() -> tuple[DaliDecoder, DecodePipeline]:
    spec_path, schema_path = _spec_paths()
    spec = load_decoder_spec(spec_path, schema_path)
    decoder = DaliDecoder(spec)
    return decoder, DecodePipeline(decoder)


def _ensure_runtime() -> None:
    if hasattr(app.state, "pipeline") and hasattr(app.state, "source_registry"):
        return
    decoder, pipeline = _build_runtime()
    app.state.decoder = decoder
    app.state.pipeline = pipeline
    app.state.source_registry = build_source_registry()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# ---- Legacy v1 endpoints (kept for compatibility) ----
def get_mock_frames() -> list[Frame]:
    return [
        Frame(timestamp="12:00:01", address="0x01", command="ON", source="mock"),
        Frame(timestamp="12:00:02", address="0x02", command="OFF", source="mock"),
        Frame(timestamp="12:00:03", address="0x03", command="DIM 50%", source="mock"),
    ]


def get_serial_frames() -> list[Frame]:
    commands = ["ON", "OFF", "DIM 25%", "DIM 50%", "DIM 75%", "QUERY"]
    addresses = ["0x01", "0x02", "0x03", "0x0A"]

    return [
        Frame(
            timestamp="live",
            address=random.choice(addresses),
            command=random.choice(commands),
            source="serial",
        )
        for _ in range(3)
    ]


@app.get("/api/frames", response_model=list[Frame])
def get_frames(source: Literal["mock", "serial"] = Query(default="mock")) -> list[Frame]:
    if source == "serial":
        return get_serial_frames()
    return get_mock_frames()


# ---- v2 decoder API ----


@app.get("/api/v2/logs", response_model=list[LogFileInfo])
def list_logs() -> list[LogFileInfo]:
    _ensure_runtime()
    registry = app.state.source_registry
    files = registry.list_simulated_logs()
    return [
        LogFileInfo(name=file.name, path=str(file), size_bytes=file.stat().st_size)
        for file in files
    ]


@app.get("/api/v2/frames", response_model=list[DecodedFrameRecord])
def get_decoded_frames(
    source: Literal["simulated_log", "serial"] = Query(default="simulated_log"),
    log_name: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=5000),
) -> list[DecodedFrameRecord]:
    _ensure_runtime()
    registry = app.state.source_registry
    pipeline: DecodePipeline = app.state.pipeline

    try:
        if source == "simulated_log":
            selected_log = log_name or "sniffer_log_example.log"
            raw_frames = registry.snapshot_simulated_log(selected_log, limit=limit)
        else:
            raw_frames = registry.snapshot_serial(limit=limit)
    except SourceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return pipeline.decode_snapshot(raw_frames)


@app.get("/api/v2/stream")
async def stream_decoded_frames(
    source: Literal["simulated_log", "serial"] = Query(default="simulated_log"),
    log_name: str | None = Query(default=None),
) -> StreamingResponse:
    _ensure_runtime()
    registry = app.state.source_registry
    pipeline: DecodePipeline = app.state.pipeline

    async def event_generator() -> AsyncIterator[str]:
        try:
            if source == "simulated_log":
                selected_log = log_name or "sniffer_log_example.log"
                raw_stream = registry.stream_simulated_log(selected_log)
            else:
                raw_stream = registry.stream_serial()

            async for record in pipeline.decode_stream(raw_stream):
                payload = record.model_dump(mode="json")
                yield f"event: frame\ndata: {json.dumps(payload)}\n\n"
        except SourceError as exc:
            yield f"event: error\ndata: {json.dumps({'detail': str(exc)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/v2/admin/reload-specs")
def reload_specs() -> dict[str, str]:
    _ensure_runtime()
    decoder, pipeline = _build_runtime()
    app.state.decoder = decoder
    app.state.pipeline = pipeline
    return {"status": "reloaded"}


def run() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)
