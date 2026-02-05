import logging
from types import SimpleNamespace

from fastapi.testclient import TestClient

from webui.app.main import app, log_capture_handler


client = TestClient(app)


def test_get_ports_defaults_to_empty_list():
    if hasattr(app, "ports"):
        delattr(app, "ports")

    response = client.get("/ports")
    assert response.status_code == 200
    assert response.json() == {"port_list": []}


def test_get_ports_returns_configured_list():
    app.ports = ["/dev/ttyUSB0", "/dev/ttyUSB1"]

    response = client.get("/ports")
    assert response.status_code == 200
    assert response.json() == {"port_list": ["/dev/ttyUSB0", "/dev/ttyUSB1"]}


def test_scan_success(monkeypatch):
    class DummyManager:
        def __init__(self, port, baudrate, parity):
            self.port = port
            self.baudrate = baudrate
            self.parity = parity

        async def scan_bus(self):
            return [
                SimpleNamespace(
                    device_name="WB-MIO",
                    firmware_version="1.2.3",
                    slave_id=2,
                    serial_num=123456,
                    baudrate=9600,
                    parity="N",
                )
            ]

    monkeypatch.setattr("webui.app.main.WirenboardModbusManager", DummyManager)

    payload = {"port": "/dev/ttyUSB0", "baudrate": [9600], "parity": ["N"]}
    response = client.post("/scan", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "slave_list": [
            {
                "slave_name": "WB-MIO",
                "firmware_version": "1.2.3",
                "slave_id": 2,
                "serial_num": 123456,
                "baudrate": 9600,
                "parity": "N",
            }
        ]
    }


def test_scan_rejects_empty_baudrate():
    payload = {"port": "/dev/ttyUSB0", "baudrate": [], "parity": ["N"]}
    response = client.post("/scan", json=payload)

    assert response.status_code == 422


def test_logs_output_returns_recent_and_clears():
    log_capture_handler.log_records.clear()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )

    log_capture_handler.log_records.append(record)

    response = client.get("/logs/output")
    assert response.status_code == 200
    data = response.json()
    assert len(data["logs"]) == 1
    assert data["logs"][0]["message"] == "hello world"

    response = client.get("/logs/output")
    assert response.status_code == 200
    assert response.json() == {"logs": []}
