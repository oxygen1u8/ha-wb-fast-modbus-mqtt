"""
Модуль, определяющий класс для представления устройства Fast Modbus.

Класс FastModbusSlave используется для хранения информации о найденном
устройстве протокола Fast Modbus.
"""


class FastModbusSlave:
    """
    Класс для представления устройства Fast Modbus.

    Хранит информацию об уникальном идентификаторе устройства, серийном номере,
    параметрах соединения и предоставляет методы для его представления.
    """

    def __init__(self, slave_id: int, serial_num: int, baudrate: int, parity: str):
        """
        Инициализирует объект FastModbusSlave.

        Args:
            slave_id (int): Идентификатор устройства
            serial_num (int): Серийный номер устройства
            baudrate (int): Скорость передачи данных
            parity (str): Тип проверки четности
        """
        self.slave_id = slave_id
        self.serial_num = serial_num
        self.baudrate = baudrate
        self.parity = parity

    def __str__(self):
        """
        Возвращает строковое представление устройства.

        Returns:
            str: Строковое представление устройства
        """
        return f"Slave ID: {hex(self.slave_id)}, Serial: {hex(self.serial_num)}, Baudrate: {self.baudrate}, Parity: {self.parity}"

    def to_dict(self):
        """
        Преобразует объект в словарь.

        Returns:
            dict: Словарь с параметрами устройства
        """
        return {
            "slave_id": self.slave_id,
            "serial_num": self.serial_num,
            "baudrate": self.baudrate,
            "parity": self.parity,
        }
