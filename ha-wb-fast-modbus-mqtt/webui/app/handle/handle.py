import asyncio
from typing import List
from app.logger import get_logger
from app.schemas.conf import PortConfiguration
from pymodbus.client import AsyncModbusSerialClient


logger = get_logger(__name__)


handle_list = []


class ModbusHandle:
    def __init__(self, port: PortConfiguration) -> None:
        self.port = port
        if self.port.port_type == "serial":
            self.modbus = AsyncModbusSerialClient(
                self.port.path,
                baudrate=self.port.baud_rate,
                bytesize=self.port.data_bits,
                parity=self.port.parity,
                timeout=float(self.port.connection_timeout_ms) / 1000.0,
                retries=self.port.connection_max_fail_cycles,
            )

    async def task_loop(self):
        while True:
            if not self.modbus.connected:
                result = await self.modbus.connect()
                if not result:
                    break

            if self.port.devices is not None:
                for device in self.port.devices:
                    if device.enabled:
                        if device.channels is not None and len(device.channels):
                            for channel in device.channels:
                                if channel.type == "input":
                                    data = await self.modbus.read_input_registers(
                                        channel.address, count=1
                                    )
                                    logger.error(data)
                                    break
