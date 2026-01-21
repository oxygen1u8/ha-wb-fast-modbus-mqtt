from .slave import FastModbusSlave


class WirenboardModbusSlave(FastModbusSlave):
    def __init__(
        self,
        device_name: str,
        firmware_version: str,
        slave_id: int,
        serial_num: int,
        baudrate: int,
        parity: str,
    ):
        self.device_name = device_name
        self.firmware_version = firmware_version
        super().__init__(slave_id, serial_num, baudrate, parity)

    def __str__(self):
        return (f"Wirenboard Device: {self.device_name}\n"
                f"Firmware Version: {self.firmware_version}\n"
                f"Slave ID: {hex(self.slave_id)} ({self.slave_id})\n"
                f"Serial Number: {hex(self.serial_num)} ({self.serial_num})\n"
                f"Baudrate: {self.baudrate} bps\n"
                f"Parity: {self.parity}")
