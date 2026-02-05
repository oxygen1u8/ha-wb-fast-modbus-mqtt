"""
Модуль, определяющий декодеры PDU для протокола Fast Modbus.

Содержит класс CustomDecodePDU, который расширяет возможности
стандартного декодера для поддержки специфичных особенностей
протокола Fast Modbus.
"""

from pymodbus.pdu.decoders import DecodePDU
from pymodbus.pdu.pdu import ModbusPDU
from pymodbus.pdu.exceptionresponse import ExceptionResponse
from pymodbus.logging import Log
from pymodbus.exceptions import ModbusException


class CustomDecodePDU(DecodePDU):
    """
    Класс декодера PDU для протокола Fast Modbus.

    Расширяет стандартный DecodePDU для поддержки специфичных возможностей
    протокола Fast Modbus от Wiren Board.
    """

    pdu_fast_modbus_table = []

    @classmethod
    def add_sub_pdu_ext(cls, req: type[ModbusPDU], resp: type[ModbusPDU]):
        """
        Добавляет PDU в таблицу для расширенной обработки.

        Args:
            req: Тип запроса PDU
            resp: Тип ответа PDU
        """
        _ = req
        if resp not in cls.pdu_fast_modbus_table:
            cls.pdu_fast_modbus_table.append(resp)

    def lookupPduClass(self, data: bytes) -> type[ModbusPDU] | None:
        """
        Определяет класс PDU по коду функции.

        Args:
            data: Данные для определения класса PDU

        Returns:
            type[ModbusPDU] | None: Класс PDU или None, если не найден
        """
        if (func_code := int(data[1])) & 0x80:
            return ExceptionResponse

        func_code = data[1]
        sub_func_code = data[2]
        for pdu in self.pdu_fast_modbus_table:
            if pdu.sub_function_code == sub_func_code:
                return pdu

        if not (pdu := self.pdu_table.get(func_code, (None, None))[self.pdu_inx]):
            return None
        if (sub_func_code := pdu.decode_sub_function_code(data)) < 0:
            return pdu
        return self.pdu_sub_table[func_code].get(sub_func_code, (None, None))[
            self.pdu_inx
        ]

    def decode(self, frame: bytes) -> ModbusPDU | None:
        """
        Декодирует фрейм в объект PDU.

        Args:
            frame: Байты фрейма для декодирования

        Returns:
            ModbusPDU | None: Декодированный объект PDU или None
        """
        try:
            if (function_code := int(frame[0])) > 0x80:
                pdu_exp = ExceptionResponse(function_code & 0x7F)
                pdu_exp.decode(frame[1:])
                return pdu_exp
            sub_func_code = int(frame[1])
            pdu = None
            for p in self.pdu_fast_modbus_table:
                if p.sub_function_code == sub_func_code:
                    pdu = p
                    break
            if pdu is None:
                Log.debug("decode PDU failed for sub_function_code {}", sub_func_code)
                raise ModbusException(f"Unknown response {function_code}")
            pdu = pdu()
            pdu.decode(frame[1:])
            # if not (pdu_class := self.pdu_table.get(function_code, (None, None))[self.pdu_inx]):
            #     Log.debug("decode PDU failed for function code {}", function_code)
            #     raise ModbusException(f"Unknown response {function_code}")
            # pdu = pdu_class()
            # pdu.decode(frame[1:])
            # if pdu.sub_function_code >= 0:
            #     lookup = self.pdu_sub_table.get(pdu.function_code, {})
            #     if sub_class := lookup.get(pdu.sub_function_code, (None,None))[self.pdu_inx]:
            #         pdu = sub_class()
            #         pdu.decode(frame[1:])
            Log.debug(
                "decoded PDU function_code({} sub {}) -> {} ",
                pdu.function_code,
                pdu.sub_function_code,
                str(pdu),
            )
            return pdu
        except (ModbusException, ValueError, IndexError) as exc:
            Log.warning("Unable to decode frame {}", exc)
        return None
