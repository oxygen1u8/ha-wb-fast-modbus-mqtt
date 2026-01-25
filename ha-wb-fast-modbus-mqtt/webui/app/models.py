from pydantic import BaseModel, Field, field_validator


class BusConfig(BaseModel):
    port: str
    baudrate: list[int] = Field()
    parity: list[str] = Field()

    @field_validator("baudrate")
    @classmethod
    def baudrate_checkup(cls, v):
        if not isinstance(v, list):
            raise ValueError("Incorrect baudrate format")
        if not len(v):
            raise ValueError("Too small baudrate list size")
        return v
    

    @field_validator("parity")
    @classmethod
    def parity_checkup(cls, v):
        if not isinstance(v, list):
            raise ValueError("Incorrect parity format")
        if not len(v):
            raise ValueError("Too small parity list size")
        return v


class DeviceInfo(BaseModel):
    slave_name: str
    firmware_version: str
    slave_id: int
    serial_num: int
    baudrate: int
    parity: str


class ResponseScan(BaseModel):
    slave_list: list[DeviceInfo] | None


class ResponsePorts(BaseModel):
    port_list: list[str]
