"""
presets/schemas.py - Modelli Pydantic v2 per validazione input/output dei preset.
"""
from __future__ import annotations

from datetime import datetime
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.pedal.schemas import PedalSchema


class PresetBase(BaseModel):
    """
    Schema base che definisce la struttura comune di un Preset.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Nome del preset (Max 50 caratteri)",
    )
    description: str | None = Field(
        None,
        max_length=512,
        description="Descrizione opzionale del preset",
    )
    effects_chain: list[PedalSchema] = Field(
        default_factory=list,
        validation_alias=AliasChoices("effects_chain", "config_json"),
        description="La catena validata dei pedali dell'effetto",
    )


class PresetCreate(PresetBase):
    """
    Payload inviato dal frontend per la creazione di un nuovo preset.
    """
    pass


class PresetUpdate(BaseModel):
    """
    Payload per l'aggiornamento parziale (PATCH) di un preset esistente.
    """
    name: str | None = Field(
        None,
        min_length=1,
        max_length=50,
        description="Nuovo nome del preset (opzionale)",
    )
    description: str | None = Field(
        None,
        max_length=512,
        description="Nuova descrizione opzionale del preset",
    )
    effects_chain: list[PedalSchema] | None = Field(
        None,
        validation_alias=AliasChoices("effects_chain", "config_json"),
        description="Nuova catena di pedali/effetti (opzionale)",
    )


class PresetOut(PresetBase):
    """
    Schema di risposta per l'esposizione del preset all'esterno.
    Supporta il parsing diretto dai modelli SQLAlchemy tramite from_attributes=True.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
