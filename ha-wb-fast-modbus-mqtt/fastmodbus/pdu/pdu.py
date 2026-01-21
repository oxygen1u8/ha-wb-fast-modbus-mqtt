"""
Модуль, определяющий базовый класс для PDU протокола Fast Modbus.

PDU (Protocol Data Unit) - это единица данных протокола, используемая
в реализации протокола Fast Modbus от Wiren Board.
"""

from pymodbus.pdu import ModbusPDU
from pymodbus.pdu.decoders import DecodePDU
from pymodbus.exceptions import ModbusIOException
from pymodbus.pdu import ModbusPDU
import struct


class FastModbusPDU(ModbusPDU):
    """
    Базовый класс для PDU протокола Fast Modbus.
    
    Расширяет стандартный ModbusPDU для поддержки специфичных возможностей
    протокола Fast Modbus от Wiren Board.
    """
    dev_id = 0xFD
    function_code = 0x46

    def __init__(
        self,
        data: bytes | None = None,
        transaction_id=0,
        address=0,
        count=0,
        bits=None,
        registers=None,
        status=1,
    ):
        """
        Инициализирует объект PDU протокола Fast Modbus.
        
        Args:
            data (bytes | None): Данные для передачи
            transaction_id: Идентификатор транзакции
            address: Адрес устройства
            count: Количество элементов
            bits: Битовые значения
            registers: Регистры
            status: Статус
        """
        self.data = data
        super().__init__(
            self.dev_id, transaction_id, address, count, bits, registers, status
        )

    def encode(self) -> bytes:
        """
        Кодирует PDU в байты для передачи.
        
        Returns:
            bytes: Закодированные данные PDU
            
        Raises:
            ModbusIOException: Если отсутствует атрибут sub_function_code
        """
        if not hasattr(self, "sub_function_code"):
            raise ModbusIOException(
                "Fast Modbus request required a 'sub_function_code' attribute"
            )
        result_data = struct.pack(">b", self.sub_function_code)
        if self.data is not None:
            result_data += struct.pack(">b", self.data)
        return result_data


