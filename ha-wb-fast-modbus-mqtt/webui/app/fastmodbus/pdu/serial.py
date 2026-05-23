from .pdu import FastModbusPDU
from pymodbus.pdu import DecodePDU
import struct


class FastModbusSerialRequest(FastModbusPDU):
    sub_function_code = 0x08
    rtu_frame_size = 14

    def __init__(
        self,
        serial_num: int,
        modbus_function_code: int,
        data=None,
        transaction_id=0,
        address=0,
        count=0,
        bits=None,
        registers=None,
        status=1,
    ):
        self.serial_num = serial_num
        self.modbus_function_code = modbus_function_code
        super().__init__(data, transaction_id, address, count, bits, registers, status)

    def encode(self):
        return struct.pack(
            ">BIBHH",
            self.sub_function_code,
            self.serial_num,
            self.modbus_function_code,
            self.address,
            self.count,
        )


class FastModbusSerialResponse(FastModbusPDU):
    sub_function_code = 0x09
    rtu_byte_count_pos = 8

    def decode(self, data: bytes):
        params = struct.unpack(">BIBB", data[:7])
        self.sub_function_code, self.serial_num = params[0:2]
        self.modbus_cmd, self.msg_size = params[2:4]

        for i in range(7, len(data), 2):
            params = struct.unpack(">H", data[i : i + 2])
            self.registers.append(params[0])

        self.data = data[7:]

    @classmethod
    def decode_sub_function_code(cls, data: bytes):
        if int(data[2]) == cls.sub_function_code:
            return 8
        return -1


DecodePDU.add_pdu(FastModbusSerialRequest, FastModbusSerialResponse)
DecodePDU.add_sub_pdu(FastModbusSerialRequest, FastModbusSerialResponse)
