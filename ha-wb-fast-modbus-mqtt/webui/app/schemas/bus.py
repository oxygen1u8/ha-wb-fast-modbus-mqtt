from pydantic import BaseModel, Field
from typing import Literal, List


class Bus(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор шины")
    name: str = Field(..., description="Название порта")
    baudrate: List[int] = Field(..., description="Доступные скорости")
    parity: List[str] = Field(..., description="Доступные биты четности")


class BusCreate(BaseModel):
    name: str = Field(..., description="Название порта")
    baudrate: List[int] = Field(..., description="Доступные скорости")
    parity: List[str] = Field(..., description="Доступные биты четности")
