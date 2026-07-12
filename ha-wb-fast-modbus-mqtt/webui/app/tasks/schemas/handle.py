import asyncio
from app.logger import get_logger
from app.schemas.device import Device
from pymodbus.client import AsyncModbusSerialClient
import json


logger = get_logger(__name__)


class ModbusHandle:
    def __init__(self, device: Device) -> None:
        self.device = device

    async def task_loop(self):
        while True:
            json_config = json.loads(self.device.config)
            if json_config["enabled"]:
                await asyncio.sleep(1)
