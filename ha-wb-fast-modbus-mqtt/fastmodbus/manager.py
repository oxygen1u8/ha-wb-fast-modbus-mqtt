from .asyncfastmodbus import AsyncFastModbusSerialClient
from .slave import FastModbusSlave
import asyncio
import logging


class FastModbusManager:
    def __init__(
        self, port: str, baudrates: list[int] = None, parity_options: list[str] = None
    ):
        self.port = port
        self.baudrates = baudrates or [115200]
        self.parity_options = parity_options or ["N", "E", "O"]
        self.clients = []

    async def scan_bus(self) -> list[FastModbusSlave]:
        """Сканирует шину на всех допустимых скоростях и битах четности"""
        all_slaves = []

        for baudrate in self.baudrates:
            for parity in self.parity_options:
                try:
                    client = AsyncFastModbusSerialClient(
                        port=self.port, baudrate=baudrate, parity=parity
                    )

                    await client.connect()
                    self.clients.append(client)

                    slaves = await client.scan()
                    all_slaves.extend(slaves)

                    client.close()
                except Exception as e:
                    logging.error(
                        f"Ошибка при сканировании с baudrate={baudrate}, parity={parity}: {e}"
                    )
                    client.close()
                    continue
        
        return all_slaves
