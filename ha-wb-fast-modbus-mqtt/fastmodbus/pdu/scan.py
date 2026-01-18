from .pdu import FastModbusPDU
from .decoders import CustomDecodePDU
from pymodbus.pdu.decoders import DecodePDU
import struct


class FastModbusScanRequest(FastModbusPDU):
    sub_function_code = 0x01
    rtu_frame_size = 5

    def __init__(self, transaction_id=0, status=1):
        super().__init__(transaction_id=transaction_id, status=status)


class FastModbusContinueScanRequest(FastModbusPDU):
    sub_function_code = 0x02
    rtu_frame_size = 5

    def __init__(self, transaction_id=0, status=1):
        super().__init__(transaction_id=transaction_id, status=status)


class FastModbusScanResponse(FastModbusPDU):
    sub_function_code = 0x03
    rtu_frame_size = 10

    def decode(self, data: bytes):
        self.serial_num, self.slave_id = struct.unpack(">IB", data[1:])


class FastModbusScanEndResponse(FastModbusPDU):
    sub_function_code = 0x04
    rtu_frame_size = 5

    def decode(self, data: bytes):
        _ = data

# CustomDecodePDU.add_pdu(FastModbusScanRequest, FastModbusScanResponse)
# CustomDecodePDU.add_pdu(FastModbusContinueScanRequest, FastModbusScanResponse)

# DecodePDU.add_sub_pdu(FastModbusScanRequest, FastModbusScanResponse)
# DecodePDU.add_sub_pdu(FastModbusContinueScanRequest, FastModbusScanResponse)
# DecodePDU.add_sub_pdu(FastModbusContinueScanRequest, FastModbusScanEndResponse)

CustomDecodePDU.add_sub_pdu_ext(FastModbusScanRequest, FastModbusScanResponse)
CustomDecodePDU.add_sub_pdu_ext(FastModbusContinueScanRequest, FastModbusScanResponse)
CustomDecodePDU.add_sub_pdu_ext(FastModbusContinueScanRequest, FastModbusScanEndResponse)
