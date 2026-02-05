import types

import pytest

from fastmodbus.manager import WirenboardModbusManager


class DummyClient:
    def __init__(self, port, baudrate, parity):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.closed = False

    async def connect(self):
        return None

    async def scan(self):
        return [
            types.SimpleNamespace(
                slave_id=1,
                serial_num=42,
                baudrate=self.baudrate,
                parity=self.parity,
            )
        ]

    async def read_input_registers_by_serial(self, serial_num, address, count):
        if address == 0xC8:
            # "DEV" as char codes
            return types.SimpleNamespace(registers=[68, 69, 86])
        if address == 0xFA:
            return types.SimpleNamespace(registers=[49, 46, 48])  # "1.0"
        return types.SimpleNamespace(registers=[])

    def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_scan_bus_collects_devices(monkeypatch):
    monkeypatch.setattr("fastmodbus.manager.AsyncFastModbusSerialClient", DummyClient)

    manager = WirenboardModbusManager(
        port="/dev/ttyUSB0", baudrates=[9600], parity_options=["N"]
    )

    slaves = await manager.scan_bus()

    assert len(slaves) == 1
    slave = slaves[0]
    assert slave.device_name == "DEV"
    assert slave.firmware_version == "1.0"
    assert slave.slave_id == 1
    assert slave.serial_num == 42
    assert slave.baudrate == 9600
    assert slave.parity == "N"
