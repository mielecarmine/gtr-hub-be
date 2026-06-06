"""
presets/models.py - Modello SQLAlchemy per i Preset.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.users.models import User


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Preset(Base):
    """
    Rappresenta un preset di effetti guitar.

    `config_json` è gestito come JSON dal driver SQLAlchemy.
    """
    __tablename__ = "presets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    client_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, unique=True, index=True
    )
    config_json: Mapped[list | dict] = mapped_column(
        JSON, nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    # Relazione N-1 con User (riferimento come stringa per evitare import circolare)
    user: Mapped["User"] = relationship("User", back_populates="presets")
