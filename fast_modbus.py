from pymodbus.client import ModbusSerialClient

BROADCAST_ADDRESS = 0xFD
FAST_MODBUS_CMD = 0x46

START_SCAN_CMD = 0x01
CONTINUE_SCAN_CMD = 0x02
RESPONSE_SCAN_CMD = 0x03
END_SCAN_CMD = 0x04


class FastModbusSerialClient(ModbusSerialClient):
    @staticmethod
    def __modbus_crc16(data: bytes) -> bytes:
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

    def __modbus_send(self, request: bytes, addr: tuple | None = None) -> int:
        _ = addr
        request += self.__modbus_crc16(request)
        return self.socket.write(request)

    def __fm_send(self, data: bytes):
        send_data = bytes([BROADCAST_ADDRESS, FAST_MODBUS_CMD]) + data
        self.__modbus_send(send_data)

    def __start_scan(self):
        self.__fm_send(bytes([START_SCAN_CMD]))

    def __scan_process(self):
        GET_DUMMY_DATA_STATE = 0
        GET_RESPONSE_MSG_STATE = 1
        ANALYZE_MSG_STATE = 2
        CONTINUE_SCAN_STATE = 3
        ERROR_STATE = 4

        DUMMY_DATA = 0xFF

        END_MSG_LEN = 5
        RESPONSE_MSG_LEN = 10

        state = GET_DUMMY_DATA_STATE

        msg = []
        expected_msg_len = RESPONSE_MSG_LEN

        get_data = lambda: (lambda b: int.from_bytes(b, "big") if b else None)(
            self.recv(1)
        )

        while True:
            if state == GET_DUMMY_DATA_STATE:
                msg.clear()
                data = get_data()
                if data is None:
                    state = ERROR_STATE
                    continue
                if data != DUMMY_DATA:
                    msg.append(data)
                    state = GET_RESPONSE_MSG_STATE

            elif state == GET_RESPONSE_MSG_STATE:
                if not hasattr(self, "slave_map"):
                    self.slave_map = {}
                while len(msg) != expected_msg_len:
                    data = get_data()
                    if data is None:
                        state = ERROR_STATE
                        continue

                    if len(msg) == 2:
                        if data == END_SCAN_CMD:
                            expected_msg_len = END_MSG_LEN
                    elif len(msg) == 1 and data != FAST_MODBUS_CMD:
                        # TODO: new state
                        state = ERROR_STATE
                    msg.append(data)
                state = ANALYZE_MSG_STATE

            elif state == ANALYZE_MSG_STATE:
                rcv_crc16 = bytes(msg[-2:])
                msg_crc16 = self.__modbus_crc16(bytes(msg[:-2]))
                if msg_crc16 != rcv_crc16:
                    raise ValueError("Wrong CRC16")

                if msg[2] == END_SCAN_CMD:
                    break
                elif msg[2] == RESPONSE_SCAN_CMD:
                    slave_id = msg[-3]
                    serial_id = bytes(msg[3:-3]).hex()
                    if slave_id not in self.slave_map.keys():
                        self.slave_map[slave_id] = serial_id
                    else:
                        if type(self.slave_map[slave_id]) != int:
                            self.slave_map[slave_id].append(serial_id)
                        else:
                            self.slave_map[slave_id] = [
                                self.slave_map[slave_id],
                                serial_id,
                            ]

                    state = CONTINUE_SCAN_STATE

            elif state == CONTINUE_SCAN_STATE:
                self.__fm_send(bytes([CONTINUE_SCAN_CMD]))
                state = GET_DUMMY_DATA_STATE

            else:
                raise ConnectionError()

    def scan(self):
        self.__start_scan()
        self.__scan_process()


client = FastModbusSerialClient("/dev/ttyACM0", baudrate=115200)
client.connect()
client.scan()
print(client.slave_map)
client.close()
# data = client.read_input_registers(0x20, count=4, device_id=115)
# print(data)
# client.close()
