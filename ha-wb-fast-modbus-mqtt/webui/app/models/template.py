from sqlalchemy import CheckConstraint, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(255))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    config: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint("json_valid(config)", name="ck_templates_config_json_valid"),
        UniqueConstraint("device_type", name="uq_templates_device_type"),
        UniqueConstraint("filename", name="uq_templates_filename"),
    )
