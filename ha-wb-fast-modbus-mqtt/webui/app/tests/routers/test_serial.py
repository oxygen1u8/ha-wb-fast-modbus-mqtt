import pytest
import asyncio
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response


def test_root(client: TestClient):
    response = client.get("/serial")
    assert response.status_code == status.HTTP_200_OK


def test_get_bus_list(client: TestClient):
    response = client.get("/serial/bus")
    assert response.status_code == status.HTTP_200_OK
