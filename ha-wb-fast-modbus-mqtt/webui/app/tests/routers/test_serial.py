import pytest
import asyncio
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from app.models.bus import Bus as BusModel
from app.schemas.bus import Bus as BusSchema


def test_root(client: TestClient):
    response = client.get("/serial")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"].startswith("text/html")
    assert "<html" in response.text.lower()


def test_get_bus_list(client: TestClient):
    response = client.get("/serial/bus")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        BusSchema(
            id=1, name="/dev/ttyRS485-1", baudrate=[9600, 115200], parity=["N"]
        ).model_dump(),
        BusSchema(
            id=2, name="/dev/ttyRS485-2", baudrate=[9600, 115200], parity=["N"]
        ).model_dump(),
    ]
