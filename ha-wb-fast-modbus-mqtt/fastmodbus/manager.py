from .asyncfastmodbus import AsyncFastModbusSerialClient
from .wbslave import WirenboardModbusSlave
import asyncio
import logging


class WirenboardModbusManager:
    def __init__(
        self, port: str, baudrates: list[int] = None, parity_options: list[str] = None
    ):
        self.port = port
        self.baudrates = baudrates or [
            1200,
            2400,
            4800,
            9600,
            19200,
            38400,
            57600,
            115200,
        ]
        self.parity_options = parity_options or ["N", "E", "O"]
        self.clients = []

    async def scan_bus(self) -> list[WirenboardModbusSlave]:
        """Сканирует шину на всех допустимых скоростях и битах четности"""
        all_slaves = []

        for baudrate in self.baudrates:
            for parity in self.parity_options:
                try:
                    client = AsyncFastModbusSerialClient(
                        port=self.port, baudrate=baudrate, parity=parity
                    )

                    await client.connect()
                    slaves = await client.scan()
                    for slave in slaves:
                        slave_name = await client.read_input_registers_by_serial(
                            slave.serial_num, 0xC8, 20
                        )
                        slave_name = "".join(chr(c) for c in slave_name.registers)
                        firmware_version = await client.read_input_registers_by_serial(
                            slave.serial_num, 0xFA, 16
                        )
                        firmware_version = "".join(chr(c) for c in firmware_version.registers)
                        all_slaves.append(
                            WirenboardModbusSlave(
                                slave_name,
                                firmware_version,
                                slave.slave_id,
                                slave.serial_num,
                                slave.baudrate,
                                slave.parity,
                            )
                        )

                    client.close()
                except Exception as e:
                    logging.error(
                        f"Ошибка при сканировании с baudrate={baudrate}, parity={parity}: {e}"
                    )
                    client.close()
                    continue

        return all_slaves
