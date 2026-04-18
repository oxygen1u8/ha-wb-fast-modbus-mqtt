from pydantic import BaseModel, Field
from typing import Literal


class Bus(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор шины")
    name: str = Field(..., description="Название порта")
    baudrate: Literal[1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200] = Field(
        ..., description="Доступные скорости"
    )
    parity: Literal["N", "E", "O"] = Field(..., description="Доступные биты четности")
