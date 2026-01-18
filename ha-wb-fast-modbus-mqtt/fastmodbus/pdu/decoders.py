from pymodbus.pdu.decoders import DecodePDU
from pymodbus.pdu.pdu import ModbusPDU
from pymodbus.pdu.exceptionresponse import ExceptionResponse
from pymodbus.logging import Log
from pymodbus.exceptions import ModbusException

class CustomDecodePDU(DecodePDU):
    pdu_fast_modbus_table = []

    @classmethod
    def add_sub_pdu_ext(cls, req: type[ModbusPDU], resp: type[ModbusPDU]):
        _ = req
        if resp not in cls.pdu_fast_modbus_table:
            cls.pdu_fast_modbus_table.append(resp)

    def lookupPduClass(self, data: bytes) -> type[ModbusPDU] | None:
        """Use `function_code` to determine the class of the PDU."""
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
        return self.pdu_sub_table[func_code].get(sub_func_code, (None, None))[self.pdu_inx]


    def decode(self, frame: bytes) -> ModbusPDU | None:
        """Decode a frame."""
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
            Log.debug("decoded PDU function_code({} sub {}) -> {} ", pdu.function_code, pdu.sub_function_code, str(pdu))
            return pdu
        except (ModbusException, ValueError, IndexError) as exc:
            Log.warning("Unable to decode frame {}", exc)
        return None
