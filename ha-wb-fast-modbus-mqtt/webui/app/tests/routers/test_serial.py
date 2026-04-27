import pytest
import asyncio
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from app.models.bus import Bus as BusModel
from app.schemas.bus import Bus as BusSchema
from app.schemas.device import Device as DeviceSchema


expect_bus_list = [
    BusSchema(
        id=1, name="/dev/ttyRS485-1", baudrate=[9600, 115200], parity=["N"]
    ).model_dump(),
    BusSchema(
        id=2, name="/dev/ttyRS485-2", baudrate=[9600, 115200], parity=["N"]
    ).model_dump(),
]
expect_device_list = [
    DeviceSchema(
        id=1,
        model="TEST-MODEL",
        slave_address=1,
        serial_num=1,
        baudrate=115200,
        bus_id=1,
        parity="N",
    ).model_dump(),
    DeviceSchema(
        id=2,
        model="TEST-MODEL",
        slave_address=2,
        serial_num=2,
        baudrate=9600,
        bus_id=1,
        parity="N",
    ).model_dump(),
    DeviceSchema(
        id=3,
        model="TEST-MODEL",
        slave_address=3,
        serial_num=3,
        baudrate=4800,
        bus_id=2,
        parity="N",
    ).model_dump(),
    DeviceSchema(
        id=4,
        model="TEST-MODEL",
        slave_address=4,
        serial_num=4,
        baudrate=1200,
        bus_id=2,
        parity="N",
    ).model_dump(),
]


def test_root(client: TestClient):
    response = client.get("/serial")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"].startswith("text/html")
    assert "<html" in response.text.lower()


def test_get_bus_list(client: TestClient):
    response = client.get("/serial/bus")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expect_bus_list


@pytest.mark.parametrize(
    "id, expect",
    [
        (1, expect_bus_list[0]),
        (2, expect_bus_list[1]),
        (3, None),
    ],
)
def test_get_bus_by_id(client: TestClient, id: int, expect: dict | None):
    response = client.get(f"/serial/bus/{id}")
    if expect is None:
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expect


def test_update_bus(client: TestClient):
    pass


@pytest.mark.parametrize(
    "id, expect",
    [
        (1, expect_device_list[0:2]),
        (2, expect_device_list[2:]),
    ],
)
def test_get_bus_devices(client: TestClient, id: int, expect: list[DeviceSchema]):
    response = client.get(f"/serial/bus/{id}/devices")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expect


def test_delete_bus_devices(client: TestClient):
    pass


def test_scan(client: TestClient):
    pass
