from pymodbus.framer import FramerRTU
from pymodbus.logging import Log


class FastScanFramerRTU(FramerRTU):
    def decode(self, data: bytes) -> tuple[int, int, int, bytes]:
        """Decode ADU."""
        self.MIN_SIZE = 5
        BROADCAST_ADDRESS = 0xFD

        data_len = len(data)
        if data_len < self.MIN_SIZE:
            Log.debug("Short frame: {} wait for more data", data, ":hex")
            return 0, 0, 0, self.EMPTY

        if BROADCAST_ADDRESS in data:
            start_pos = data.index(BROADCAST_ADDRESS)
        else:
            Log.debug("FB: Dummy data format: {}", data, ":hex")
            return 0, 0, 0, self.EMPTY

        for used_len in range(start_pos, data_len):
            if data_len - used_len < self.MIN_SIZE:
                Log.debug("Short frame: {} wait for more data", data, ":hex")
                return 0, 0, 0, self.EMPTY
            dev_id = int(data[used_len])
            if not (pdu_class := self.decoder.lookupPduClass(data[used_len:])):
                continue
            if not (size := pdu_class.calculateRtuFrameSize(data[used_len:])):
                Log.debug("Frame - rtu_byte_count_pos wrong")
                return 0, dev_id, 0, self.EMPTY
            if data_len < used_len +size:
                Log.debug("Frame - not ready")
                return 0, dev_id, 0, self.EMPTY
            for test_len in range(data_len, used_len + size - 1, -1):
                start_crc = test_len -2
                crc = data[start_crc : start_crc + 2]
                crc_val = (int(crc[0]) << 8) + int(crc[1])
                if not FramerRTU.check_CRC(data[used_len : start_crc], crc_val):
                    Log.debug("Frame check failed, possible garbage after frame, testing..")
                    continue
                return data_len, dev_id, 0, data[used_len + 1 : start_crc]
        return 0, 0, 0, self.EMPTY
