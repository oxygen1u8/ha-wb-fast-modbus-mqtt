from sqlalchemy import Integer, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ModbusConfigurationModel(Base):
    __tablename__ = "modbus_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config: Mapped[str] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("json_valid(config)", name="ck_devices_config_json_valid"),
    )
