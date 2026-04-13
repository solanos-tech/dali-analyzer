from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frames_mock_response_shape() -> None:
    response = client.get("/api/frames", params={"source": "mock"})
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 3

    for frame in payload:
        assert set(frame.keys()) == {"timestamp", "address", "command", "source"}
        assert frame["source"] == "mock"


def test_frames_serial_response_shape() -> None:
    response = client.get("/api/frames", params={"source": "serial"})
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 3

    for frame in payload:
        assert set(frame.keys()) == {"timestamp", "address", "command", "source"}
        assert frame["source"] == "serial"


def test_frames_invalid_source() -> None:
    response = client.get("/api/frames", params={"source": "invalid"})
    assert response.status_code == 422
