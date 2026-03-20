"""
schemas.py - Modelli Pydantic per validazione input/output.

Rispecchiano l'interfaccia TypeScript del frontend:
  - id, name, author_id, chain (lista di EffectNode)
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ===================================================================
# Effect Chain
# ===================================================================

class EffectParams(BaseModel):
    """Parametri liberi per un singolo effetto (key-value arbitrari)."""
    model_config = ConfigDict(extra="allow")

    # I campi comuni sono opzionali – il frontend può inviare qualsiasi param
    # (gain, decay, rate, distortion, ecc.)


class EffectNode(BaseModel):
    """
    Nodo nella catena di effetti.

    Corrisponde all'interfaccia TypeScript:
        interface EffectNode {
          type: string;
          position: number;
          params: Record<string, unknown>;
        }
    """
    type: str = Field(..., description="Tipo di effetto (es. 'Reverb', 'Distortion')")
    position: int = Field(..., ge=0, description="Posizione ordinata nella catena")
    params: dict[str, Any] = Field(default_factory=dict, description="Parametri specifici del nodo")


# ===================================================================
# User
# ===================================================================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: str = Field(..., max_length=256)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ===================================================================
# Preset
# ===================================================================

class PresetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)


class PresetCreate(PresetBase):
    """Payload inviato dal frontend per creare un preset."""
    chain: list[EffectNode] = Field(default_factory=list)


class PresetUpdate(BaseModel):
    """Payload per aggiornamento parziale (PATCH)."""
    name: str | None = Field(None, min_length=1, max_length=128)
    chain: list[EffectNode] | None = None


class PresetRead(PresetBase):
    """Risposta al frontend, include chain deserializzata."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    chain: list[EffectNode]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_preset(cls, preset) -> "PresetRead":  # type: ignore[override]
        """Costruisce il modello leggendo il property `chain` dell'ORM."""
        return cls(
            id=preset.id,
            name=preset.name,
            author_id=preset.author_id,
            chain=[EffectNode(**node) for node in preset.chain],
            created_at=preset.created_at,
            updated_at=preset.updated_at,
        )
