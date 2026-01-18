from pymodbus.client import AsyncModbusSerialClient
from pymodbus.pdu.decoders import DecodePDU
from pymodbus.exceptions import ModbusIOException
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


class AsyncFastModbusSerialClient(AsyncModbusSerialClient):
    async def scan(self):
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
                    self.comm_params.stopbits,
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
                        self.comm_params.stopbits,
                    )
                )
        except:
            # traceback.print_exc()

            return []
        finally:
            self.ctx.retries = base_retries
            self.ctx.framer = base_framer

            return slave_map
