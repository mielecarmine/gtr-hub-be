"""
models.py - Tabelle SQLAlchemy: User e Preset.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# -------------------------------------------------------------------
# User
# -------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(256), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    # Relazione 1-N con Preset
    presets: Mapped[list["Preset"]] = relationship(
        "Preset", back_populates="user", cascade="all, delete-orphan"
    )


# -------------------------------------------------------------------
# Preset
# -------------------------------------------------------------------
class Preset(Base):
    """
    Rappresenta un preset di effetti guitar.

    `config_json` è gestito come JSON dal driver SQLAlchemy:
    in SQLite viene serializzato come stringa; Python lo vede
    sempre come list[dict] (la catena di pedali/effetti).

    Esempio di valore:
        [
            {"id": "dist-1", "type": "distortion", "position": 0,
             "params": {"gain": 0.8, "tone": 0.5}},
            {"id": "rev-1",  "type": "reverb",     "position": 1,
             "params": {"decay": 2.0, "wet": 0.3}}
        ]
    """
    __tablename__ = "presets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    config_json: Mapped[list | dict] = mapped_column(
        JSON, nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    # Relazione N-1 con User
    user: Mapped["User"] = relationship("User", back_populates="presets")
