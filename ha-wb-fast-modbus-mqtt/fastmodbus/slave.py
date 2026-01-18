class FastModbusSlave:
    def __init__(
        self, slave_id: int, serial_num: int, baudrate: int, parity: str, stop: int
    ):
        self.slave_id = slave_id
        self.serial_num = serial_num
        self.baudrate = baudrate
        self.parity = parity
        self.stop = stop


    def __str__(self):
        return f"{hex(self.slave_id)} | {hex(self.serial_num)} | {(self.baudrate)} | {self.parity}"
