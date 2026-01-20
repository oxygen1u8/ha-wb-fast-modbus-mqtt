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

    async def scan(self) -> list[FastModbusSlave]:
        """
        Выполняет сканирование шины Modbus для обнаружения устройств.

        Returns:
            list: Список объектов FastModbusSlave, представляющих найденные устройства
        """
        original_framer = self.ctx.framer
        original_retries = self.ctx.retries

        try:
            # Настраиваем фреймер для сканирования
            decoder = self.ctx.framer.decoder
            self.ctx.retries = 0
            self.ctx.framer = FastScanFramerRTU(decoder)
            self.ctx.framer.decoder = CustomDecodePDU(False)

            slave_map = []
            first_request = True

            while True:
                # Первый запрос сканирования или продолжение сканирования
                try:
                    if not first_request:
                        request = FastModbusContinueScanRequest()
                    else:
                        request = FastModbusScanRequest()
                        first_request = False

                    result = await self.execute(
                        request=request, no_response_expected=False
                    )

                    # Проверяем, завершено ли сканирование
                    if isinstance(result, FastModbusScanEndResponse):
                        break

                    slave_map.append(
                        FastModbusSlave(
                            result.slave_id,
                            result.serial_num,
                            self.comm_params.baudrate,
                            self.comm_params.parity,
                        )
                    )
                except (
                    ModbusIOException,
                    ConnectionException,
                    asyncio.TimeoutError,
                ) as e:
                    logging.error(f"Ошибка при выполнении запроса сканирования: {e}")
                    break
        except (
            ModbusIOException,
            ConnectionException,
            asyncio.TimeoutError,
            Exception,
        ) as e:
            logging.error(f"Ошибка при сканировании шины Modbus: {e}")
        finally:
            # Восстанавливаем оригинальные параметры
            self.ctx.retries = original_retries
            self.ctx.framer = original_framer

            return slave_map
