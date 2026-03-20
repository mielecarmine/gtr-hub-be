"""
models.py - Tabelle SQLAlchemy: User e Preset.
"""
import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
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
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    # Relazione 1-N con Preset
    presets: Mapped[list["Preset"]] = relationship(
        "Preset", back_populates="author", cascade="all, delete-orphan"
    )


# -------------------------------------------------------------------
# Preset
# -------------------------------------------------------------------
class Preset(Base):
    """
    Rappresenta un preset di effetti.

    Il campo `config` è una stringa JSON che serializza la chain di effetti,
    ad es.:
        [{"type": "Reverb", "position": 1, "params": {"decay": 2.5}}, ...]
    """
    __tablename__ = "presets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    config: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    # Relazione N-1 con User
    author: Mapped["User"] = relationship("User", back_populates="presets")

    # -------------------------------------------------------------------
    # Helper: accesso tipizzato alla chain JSON
    # -------------------------------------------------------------------
    @property
    def chain(self) -> list[dict]:
        """Deserializza il campo config come lista Python."""
        try:
            return json.loads(self.config)
        except (json.JSONDecodeError, TypeError):
            return []

    @chain.setter
    def chain(self, value: list[dict]) -> None:
        """Serializza una lista Python nel campo config."""
        self.config = json.dumps(value, ensure_ascii=False)
