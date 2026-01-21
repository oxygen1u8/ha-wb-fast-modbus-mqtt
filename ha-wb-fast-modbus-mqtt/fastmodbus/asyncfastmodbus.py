"""
Асинхронный клиент для работы с протоколом Fast Modbus от Wiren Board.

Модуль предоставляет класс AsyncFastModbusSerialClient, который расширяет
функциональность стандартного AsyncModbusSerialClient для поддержки
специфичных возможностей протокола Fast Modbus.
"""

from pymodbus.client import AsyncModbusSerialClient
from pymodbus.pdu.decoders import DecodePDU
from pymodbus.exceptions import ModbusIOException, ConnectionException
from .pdu.scan import (
    FastModbusScanRequest,
    FastModbusContinueScanRequest,
    FastModbusScanEndResponse,
)
from .pdu.serial import FastModbusSerialRequest, FastModbusSerialResponse
from .pdu.decoders import CustomDecodePDU
from .rtu.scan import FastScanFramerRTU
from .slave import FastModbusSlave
import asyncio
import traceback
import logging


class AsyncFastModbusSerialClient(AsyncModbusSerialClient):
    """
    Асинхронный клиент для протокола Fast Modbus.

    Расширяет стандартный AsyncModbusSerialClient для поддержки специфичных
    возможностей протокола Fast Modbus от Wireн Board.
    """

    async def read_input_registers_by_serial(
        self,
        serial_num: int,
        address: int,
        count: int = 1,
        no_response_expected: bool = False,
    ):
        
        # self.read_input_registers()
        return await self.execute(
            no_response_expected,
            FastModbusSerialRequest(
                serial_num=serial_num,
                address=address,
                modbus_function_code=0x04,
                count=count,
            )
        )

    async def scan(self) -> list[FastModbusSlave]:
        """
        Выполняет сканирование шины Modbus для обнаружения устройств.

        Returns:
            list: Список объектов FastModbusSlave, представляющих найденные устройства
        """
        base_framer = self.ctx.framer
        base_retries = self.ctx.retries
        decoder = self.ctx.framer.decoder

        self.ctx.retries = 0
        self.ctx.framer = FastScanFramerRTU(decoder)
        self.ctx.framer.decoder = CustomDecodePDU(False)

        slave_map = []

        try:
            result = await self.execute(
                request=FastModbusScanRequest(), no_response_expected=False
            )
            slave_map.append(
                FastModbusSlave(
                    result.slave_id,
                    result.serial_num,
                    self.comm_params.baudrate,
                    self.comm_params.parity,
                )
            )
            while True:
                result = await self.execute(
                    request=FastModbusContinueScanRequest(), no_response_expected=False
                )
                if type(result) is FastModbusScanEndResponse:
                    break
                slave_map.append(
                    FastModbusSlave(
                        result.slave_id,
                        result.serial_num,
                        self.comm_params.baudrate,
                        self.comm_params.parity,
                    )
                )
        except Exception as e:
            # traceback.print_exc()
            print(f"GOT IT: {e}")
            return []
        finally:
            self.ctx.retries = base_retries
            self.ctx.framer = base_framer

            return slave_map
