from fastapi.datastructures import Default
from pydantic import BaseModel, Field
from typing import Literal, List, Optional


class DeviceChannelConfiguration(BaseModel):
    name: str = Field()
    id: Optional[str] = Field(default=None)
    enabled: Optional[bool] = Field(default=False)
    reg_type: Optional[str] = Field(default="input")
    address: int = Field()
    type: Optional[str] = Field(default="value")
    format: Optional[str] = Field(default="u16")
    word_order: Optional[str] = Field(default="big_endian")
    byte_order: Optional[str] = Field(default="big_endian")
    scale: Optional[float] = Field(default=0.0)
    offset: Optional[float] = Field(default=0.0)
    round_to: Optional[float] = Field(default=0.0)


class DeviceConfiguration(BaseModel):
    device_model: Optional[str] = Field()
    name: Optional[str] = Field()
    id: str = Field()
    slave_id: Optional[int] = Field(default=0xFF)
    enabled: Optional[bool] = Field(default=True)
    channels: Optional[List[DeviceChannelConfiguration]] = Field(default=[])


class DeviceConfigurationRequest(BaseModel):
    port_path: str = Field(..., description="")
    device_id: str = Field(..., description="")


class DeviceSetConfigurationRequest(BaseModel):
    port_path: str = Field(..., description="")
    config: DeviceConfiguration = Field(..., description="")


class PortConfiguration(BaseModel):
    port_type: str = Field(default="serial", description="")
    path: str = Field()
    baud_rate: int = Field()
    parity: Literal["N", "E", "O"] = Field(default="N")
    data_bits: int = Field(default=8)
    stop_bits: int = Field(default=0)
    response_timeout_ms: int = Field(default=500)
    guard_interval_us: int = Field(default=1000)
    connection_timeout_ms: int = Field(default=5000)
    connection_max_fail_cycles: int = Field(default=2)
    enabled: bool = Field(default=True)
    devices: List[DeviceConfiguration] = Field(default=[], description="")


class ModbusConfiguration(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор конфигурации Modbus")
    debug: bool = Field(
        default=False, description="Включение/выключение отладочной печати"
    )
    max_unchanged_interval: int = Field(default=-1, description="")
    rate_limit: int = Field(100, description="")
    ports: List[PortConfiguration] = Field(default=[], description="")


class ModbusConfigurationCreate(BaseModel):
    debug: bool = Field(
        default=False, description="Включение/выключение отладочной печати"
    )
    max_unchanged_interval: int = Field(default=-1, description="")
    rate_limit: int = Field(default=100, description="")
    ports: List[PortConfiguration] = Field(default=[], description="")
