"""
Модуль, определяющий классы PDU для операций сканирования протокола Fast Modbus.

Содержит классы запросов и ответов, используемых при сканировании шины
для обнаружения устройств протокола Fast Modbus.
"""

from .pdu import FastModbusPDU
from .decoders import CustomDecodePDU
import struct


class FastModbusScanRequest(FastModbusPDU):
    """
    Класс для запроса сканирования устройств Fast Modbus.
    """
    sub_function_code = 0x01
    rtu_frame_size = 5

    def __init__(self, transaction_id=0, status=1):
        """
        Инициализирует запрос сканирования.
        
        Args:
            transaction_id: Идентификатор транзакции
            status: Статус запроса
        """
        super().__init__(transaction_id=transaction_id, status=status)


class FastModbusContinueScanRequest(FastModbusPDU):
    """
    Класс для запроса продолжения сканирования устройств Fast Modbus.
    """
    sub_function_code = 0x02
    rtu_frame_size = 5

    def __init__(self, transaction_id=0, status=1):
        """
        Инициализирует запрос продолжения сканирования.
        
        Args:
            transaction_id: Идентификатор транзакции
            status: Статус запроса
        """
        super().__init__(transaction_id=transaction_id, status=status)


class FastModbusScanResponse(FastModbusPDU):
    """
    Класс для ответа на запрос сканирования устройств Fast Modbus.
    """
    sub_function_code = 0x03
    rtu_frame_size = 10

    def decode(self, data: bytes):
        """
        Декодирует данные ответа.
        
        Args:
            data (bytes): Данные для декодирования
        """
        self.serial_num, self.slave_id = struct.unpack(">IB", data[1:])


class FastModbusScanEndResponse(FastModbusPDU):
    """
    Класс для ответа об окончании сканирования Fast Modbus.
    """
    sub_function_code = 0x04
    rtu_frame_size = 5

    def decode(self, data: bytes):
        """
        Декодирует данные ответа.
        
        Args:
            data (bytes): Данные для декодирования
        """
        _ = data

CustomDecodePDU.add_sub_pdu_ext(FastModbusScanRequest, FastModbusScanResponse)
CustomDecodePDU.add_sub_pdu_ext(FastModbusContinueScanRequest, FastModbusScanResponse)
CustomDecodePDU.add_sub_pdu_ext(FastModbusContinueScanRequest, FastModbusScanEndResponse)
