from typing import List
from sqlalchemy import String, Integer, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Bus(Base):
    __tablename__ = "bus"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    baudrate: Mapped[List[int]] = mapped_column(ARRAY(Integer))
    parity: Mapped[List[str]] = mapped_column(ARRAY(String))
    devices: Mapped[List["Device"]] = relationship("Device", back_populates="bus")
