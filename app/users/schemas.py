"""
users/schemas.py - Modelli Pydantic v2 per validazione input/output degli utenti.
"""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: str = Field(..., max_length=256)


class UserCreate(UserBase):
    """Payload per la registrazione di un nuovo utente."""
    password: str = Field(..., min_length=8)


class UserOut(UserBase):
    """Schema di risposta per l'anagrafica utente."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
