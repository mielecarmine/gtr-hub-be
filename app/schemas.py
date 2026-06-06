"""
schemas.py - Modelli Pydantic v2 per validazione input/output dell'API.

Convenzioni di naming:
  - *Create  → payload in ingresso per creare una risorsa
  - *Update  → payload in ingresso per aggiornamento parziale (PATCH)
  - *Out     → risposta verso il frontend
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ===================================================================
# Pedale / Effetto singolo
# ===================================================================

class PedalConfig(BaseModel):
    """
    Definisce un singolo pedale nella catena di effetti.

    Corrisponde all'interfaccia TypeScript:
        interface EffectNode {
          id: string;
          type: string;
          position: number;
          params: Record<string, unknown>;
        }
    """
    id: str = Field(..., description="Identificatore univoco del pedale (es. 'dist-1')")
    type: str = Field(..., description="Tipo di effetto (es. 'distortion', 'reverb')")
    position: int = Field(..., ge=0, description="Posizione ordinata nella catena (0-based)")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Parametri specifici del pedale (gain, decay, wet, ecc.)",
    )


# ===================================================================
# User
# ===================================================================

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


# ===================================================================
# Preset
# ===================================================================

class PresetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = Field(None, max_length=512)


class PresetCreate(PresetBase):
    """Payload inviato dal frontend per creare un preset."""
    config_json: list[PedalConfig] = Field(
        default_factory=list,
        description="Catena completa di pedali/effetti",
    )


class PresetUpdate(BaseModel):
    """Payload per aggiornamento parziale (PATCH) di un preset."""
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = Field(None, max_length=512)
    config_json: list[PedalConfig] | None = None


class PresetOut(PresetBase):
    """Schema di risposta completo, include ID, timestamp e catena effetti."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    config_json: list[PedalConfig]
    created_at: datetime
