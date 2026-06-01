from sqlalchemy import String, Integer, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slave_address: Mapped[int] = mapped_column(Integer)
    serial_num: Mapped[int] = mapped_column(Integer, unique=True)
    baudrate: Mapped[int] = mapped_column(Integer)
    parity: Mapped[str] = mapped_column(String(1))
    config: Mapped[str] = mapped_column(Text, nullable=False)
    itf_name: Mapped[str] = mapped_column(String)

    bus_id: Mapped[int] = mapped_column(ForeignKey("bus.id"), nullable=False)
    bus: Mapped["Bus"] = relationship("Bus", back_populates="devices")

    __table_args__ = (
        CheckConstraint("json_valid(config)", name="ck_devices_config_json_valid"),
    )
