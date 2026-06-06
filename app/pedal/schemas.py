"""
pedal/schemas.py - Modelli Pydantic v2 per la validazione dei singoli pedali.
"""
from typing import Literal
from pydantic import BaseModel, Field

# Unione piana per i valori dei parametri dei pedali, previene nidificazioni.
PedalParamValue = int | float | bool | str

# Tipi di pedale supportati da contratto.
PedalType = Literal["distortion", "delay", "reverb", "amplifier", "chorus"]


class PedalSchema(BaseModel):
    """
    Rappresenta un singolo effetto all'interno della catena audio.
    """
    id: str = Field(
        ...,
        description="UUID o stringa univoca generata dal frontend",
        min_length=1,
    )
    type: PedalType = Field(
        ...,
        description="Tipo di effetto supportato (es. 'distortion', 'delay', etc.)",
    )
    order_index: int = Field(
        ...,
        ge=0,
        description="La posizione del pedale nella catena (0-based)",
    )
    bypass: bool = Field(
        ...,
        description="Se l'effetto è attivo o spento (bypassato)",
    )
    params: dict[str, PedalParamValue] = Field(
        default_factory=dict,
        description="Dizionario piatto di parametri variabili del pedale",
    )
