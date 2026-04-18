from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model: Mapped[str] = mapped_column(String(10))
    serial_num: Mapped[int] = mapped_column(Integer)
    baudrate: Mapped[int] = mapped_column(Integer)
    parity: Mapped[str] = mapped_column(String(1))
    bus_id: Mapped[int] = mapped_column(ForeignKey("bus.id"), nullable=False)

    bus: Mapped["Bus"] = relationship("Bus", back_populates="devices")
