from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class Device(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор устройства")
    model: str = Field(..., description="Модель")
    slave_address: int = Field(..., description="Slave адрес")
    serial_num: int = Field(..., description="Серийный номер")
    baudrate: int = Field(..., description="Скорость")
    parity: Literal["N", "E", "O"] = Field(..., description="Биты четности")
