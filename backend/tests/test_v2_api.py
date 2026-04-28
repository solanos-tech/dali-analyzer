from pathlib import Path

from app.decoder import DaliDecoder, DecodePipeline, load_decoder_spec
from app.decoder.models import RawFrame, SerialConnectionStatus, SerialPortInfo
from app.decoder.sources import RuntimeSourceConfig, SourceError, SourceRegistry
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _install_test_log_registry(tmp_path: Path) -> None:
    spec = load_decoder_spec(
        Path("app/specs/dali_decoder.json"),
        Path("app/specs/dali_decoder.schema.json"),
    )
    app.state.pipeline = DecodePipeline(DaliDecoder(spec))
    log_file = tmp_path / "sniffer_log_example.log"
    log_file.write_text(
        "\n".join(
            [
                "[2026-01-01 00:00:00.000] sniffer ts_ms=100 dir=rx_forward16 raw=0xFF91",
                "[2026-01-01 00:00:00.020] sniffer ts_ms=120 dir=rx_backward raw=0xFF",
                "[2026-01-01 00:00:00.050] sniffer ts_ms=150 dir=rx_forward24 raw=0x01FE30",
                "[2026-01-01 00:00:00.070] sniffer ts_ms=170 dir=rx_backward raw=0x22",
                "[2026-01-01 00:00:00.090] sniffer ts_ms=190 dir=rx_forward24 raw=0x01FE3C",
            ]
        ),
        encoding="utf-8",
    )
    app.state.source_registry = SourceRegistry(
        RuntimeSourceConfig(
            simulated_logs_dir=tmp_path,
            serial_port=None,
            serial_baudrate=115200,
        )
    )


def _install_dummy_serial_registry() -> None:
    spec = load_decoder_spec(
        Path("app/specs/dali_decoder.json"),
        Path("app/specs/dali_decoder.schema.json"),
    )
    app.state.pipeline = DecodePipeline(DaliDecoder(spec))
    app.state.source_registry = _DummySerialRegistry()


class _DummySerialRegistry:
    def __init__(self) -> None:
        self._connected = False
        self._port: str | None = None
        self._baudrate: int | None = None

    def list_serial_ports(self) -> list[SerialPortInfo]:
        return [
            SerialPortInfo(name="COM3", description="USB Serial Device"),
            SerialPortInfo(name="COM4", description="Virtual Serial Device"),
        ]

    def connect_serial(self, port: str, baudrate: int | None = None) -> SerialConnectionStatus:
        if port not in {"COM3", "COM4"}:
            raise SourceError("Serial port unavailable")
        self._connected = True
        self._port = port
        self._baudrate = baudrate or 115200
        return SerialConnectionStatus(
            connected=True,
            port=self._port,
            baudrate=self._baudrate,
            message="Connected",
        )

    def disconnect_serial(self) -> SerialConnectionStatus:
        old_port = self._port
        old_baudrate = self._baudrate
        self._connected = False
        self._port = None
        self._baudrate = None
        return SerialConnectionStatus(
            connected=False,
            port=old_port,
            baudrate=old_baudrate,
            message="Disconnected",
        )

    def serial_status(self) -> SerialConnectionStatus:
        return SerialConnectionStatus(
            connected=self._connected,
            port=self._port,
            baudrate=self._baudrate,
            message="Connected" if self._connected else "Disconnected",
        )

    def snapshot_serial(self, limit: int) -> list[RawFrame]:
        if not self._connected:
            raise SourceError("Serial port is not connected")
        return [
            RawFrame(
                ts_ms=index * 10,
                direction="rx_forward24",
                bit_length=24,
                raw_hex="0x01FE30",
                source="serial",
                log_name=None,
            )
            for index in range(limit)
        ]

    async def stream_serial(self):  # type: ignore[no-untyped-def]
        if not self._connected:
            raise SourceError("Serial port is not connected")
        yield RawFrame(
            ts_ms=1,
            direction="rx_forward24",
            bit_length=24,
            raw_hex="0x01FE30",
            source="serial",
            log_name=None,
        )


def test_v2_logs_endpoint(tmp_path: Path) -> None:
    _install_test_log_registry(tmp_path)
    response = client.get("/api/v2/logs")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)
    assert any(item["name"] == "sniffer_log_example.log" for item in payload)


def test_v2_frames_simulated_shape(tmp_path: Path) -> None:
    _install_test_log_registry(tmp_path)
    response = client.get(
        "/api/v2/frames",
        params={"source": "simulated_log", "log_name": "sniffer_log_example.log", "limit": 5},
    )
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 5

    first = payload[0]
    assert set(first.keys()) == {"raw", "decoded", "transaction"}
    assert first["raw"]["source"] == "simulated_log"


def test_v2_frames_simulated_prefers_24bit_window(tmp_path: Path) -> None:
    spec = load_decoder_spec(
        Path("app/specs/dali_decoder.json"),
        Path("app/specs/dali_decoder.schema.json"),
    )
    app.state.pipeline = DecodePipeline(DaliDecoder(spec))

    log_file = tmp_path / "sniffer_log_example.log"
    lines: list[str] = []
    ts = 0
    for _ in range(12):
        lines.append(f"[2026-01-01 00:00:00.000] sniffer ts_ms={ts} dir=rx_forward16 raw=0xFF91")
        ts += 10
    for _ in range(12):
        lines.append(f"[2026-01-01 00:00:00.000] sniffer ts_ms={ts} dir=rx_forward24 raw=0x01FE30")
        ts += 10
    log_file.write_text("\n".join(lines), encoding="utf-8")

    app.state.source_registry = SourceRegistry(
        RuntimeSourceConfig(
            simulated_logs_dir=tmp_path,
            serial_port=None,
            serial_baudrate=115200,
        )
    )

    response = client.get(
        "/api/v2/frames",
        params={"source": "simulated_log", "log_name": "sniffer_log_example.log", "limit": 8},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 8
    assert all(item["raw"]["direction"] == "rx_forward24" for item in payload)


def test_v2_frames_serial_shape() -> None:
    _install_dummy_serial_registry()
    connect_response = client.post("/api/v2/serial/connect", json={"port": "COM3"})
    assert connect_response.status_code == 200

    response = client.get("/api/v2/frames", params={"source": "serial", "limit": 4})
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 4
    assert all(item["raw"]["source"] == "serial" for item in payload)


def test_v2_serial_ports_endpoint() -> None:
    _install_dummy_serial_registry()
    response = client.get("/api/v2/serial/ports")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["name"] == "COM3"


def test_v2_serial_connect_disconnect_status() -> None:
    _install_dummy_serial_registry()

    status_before = client.get("/api/v2/serial/status")
    assert status_before.status_code == 200
    assert status_before.json()["connected"] is False

    connect_response = client.post("/api/v2/serial/connect", json={"port": "COM3"})
    assert connect_response.status_code == 200
    assert connect_response.json()["connected"] is True

    status_after = client.get("/api/v2/serial/status")
    assert status_after.status_code == 200
    assert status_after.json()["connected"] is True

    disconnect_response = client.post("/api/v2/serial/disconnect")
    assert disconnect_response.status_code == 200
    assert disconnect_response.json()["connected"] is False


def test_v2_serial_frames_require_connection() -> None:
    _install_dummy_serial_registry()
    response = client.get("/api/v2/frames", params={"source": "serial", "limit": 3})
    assert response.status_code == 409


def test_v2_frames_missing_log_returns_404(tmp_path: Path) -> None:
    _install_test_log_registry(tmp_path)
    response = client.get(
        "/api/v2/frames",
        params={"source": "simulated_log", "log_name": "missing.log", "limit": 3},
    )
    assert response.status_code == 404


def test_v2_stream_emits_frame_event() -> None:
    spec = load_decoder_spec(
        Path("app/specs/dali_decoder.json"),
        Path("app/specs/dali_decoder.schema.json"),
    )
    app.state.pipeline = DecodePipeline(DaliDecoder(spec))

    class _DummyRegistry:
        async def stream_simulated_log(self, log_name: str):  # type: ignore[no-untyped-def]
            yield RawFrame(
                ts_ms=1,
                direction="rx_forward16",
                bit_length=16,
                raw_hex="0xFF91",
                source="simulated_log",
                log_name=log_name,
            )

        async def stream_serial(self):  # type: ignore[no-untyped-def]
            yield RawFrame(
                ts_ms=1,
                direction="rx_forward16",
                bit_length=16,
                raw_hex="0xFF91",
                source="serial",
                log_name=None,
            )

    app.state.source_registry = _DummyRegistry()

    with client.stream(
        "GET",
        "/api/v2/stream",
        params={"source": "simulated_log", "log_name": "sniffer_log_example.log"},
    ) as response:
        assert response.status_code == 200
        seen_event = False
        for chunk in response.iter_raw():
            if b"event: frame" in chunk:
                seen_event = True
                break

        assert seen_event


def test_reload_specs_endpoint() -> None:
    response = client.post("/api/v2/admin/reload-specs")
    assert response.status_code == 200
    assert response.json() == {"status": "reloaded"}
