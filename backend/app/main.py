import os
import random
from typing import Literal

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


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
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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


def run() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)
