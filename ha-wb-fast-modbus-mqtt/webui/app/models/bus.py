from typing import List
from sqlalchemy import String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Bus(Base):
    __tablename__ = "bus"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    baudrate: Mapped[List[int]] = mapped_column(JSON, nullable=False, default=List)
    parity: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=List)
