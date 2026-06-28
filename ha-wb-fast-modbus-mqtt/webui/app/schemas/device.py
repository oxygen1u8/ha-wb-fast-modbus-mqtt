from pydantic import BaseModel, Field
from typing import Literal

from sqlalchemy import desc


class Device(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор устройства")
    slave_address: int = Field(..., description="Slave адрес")
    serial_num: int = Field(..., description="Серийный номер")
    baudrate: int = Field(..., description="Скорость")
    parity: Literal["N", "E", "O"] = Field(..., description="Биты четности")
    config: str = Field(..., description="JSON конфигурация")
    itf_name: str = Field(..., description="Название интерфейса")
    bus_id: int = Field(..., description="Номер шины")


class DeviceCreate(BaseModel):
    slave_address: int = Field(..., description="Slave адрес")
    serial_num: int = Field(..., description="Серийный номер")
    baudrate: int = Field(..., description="Скорость")
    parity: Literal["N", "E", "O"] = Field(..., description="Биты четности")
    config: str = Field(..., description="JSON конфигурация")
    itf_name: str = Field(..., description="Название интерфейса")
    bus_id: int = Field(..., description="Номер шины")


class DeviceListDelete(BaseModel):
    devices_id: list[int]
