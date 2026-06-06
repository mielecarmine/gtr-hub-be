"""
presets/router.py - Endpoint CRUD per i Preset.
"""
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.presets.models import Preset
from app.presets.schemas import PresetCreate, PresetOut, PresetUpdate

router = APIRouter(prefix="/presets", tags=["Presets"])


# -------------------------------------------------------------------
# GET /presets  – lista tutti i preset (filtrabili per user_id)
# -------------------------------------------------------------------
@router.get("/", response_model=list[PresetOut])
async def list_presets(
    user_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> Sequence[Preset]:
    stmt = select(Preset)
    if user_id is not None:
        stmt = stmt.where(Preset.user_id == user_id)
    result = await db.execute(stmt)
    presets = result.scalars().all()
    return presets


# -------------------------------------------------------------------
# GET /presets/{id}  – singolo preset
# -------------------------------------------------------------------
@router.get("/{preset_id}", response_model=PresetOut)
async def get_preset(preset_id: int, db: AsyncSession = Depends(get_db)) -> Preset:
    preset = await db.get(Preset, preset_id)
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    return preset


# -------------------------------------------------------------------
# POST /presets  – crea un nuovo preset
# -------------------------------------------------------------------
@router.post("/", response_model=PresetOut, status_code=status.HTTP_201_CREATED)
async def create_preset(
    body: PresetCreate,
    user_id: int,          # in futuro sostituire con JWT dependency
    db: AsyncSession = Depends(get_db),
) -> Preset:
    preset = Preset(
        name=body.name,
        description=body.description,
        user_id=user_id,
        config_json=[pedal.model_dump() for pedal in body.config_json],
    )
    db.add(preset)
    await db.flush()
    await db.refresh(preset)
    return preset


# -------------------------------------------------------------------
# PATCH /presets/{id}  – aggiornamento parziale
# -------------------------------------------------------------------
@router.patch("/{preset_id}", response_model=PresetOut)
async def update_preset(
    preset_id: int,
    body: PresetUpdate,
    db: AsyncSession = Depends(get_db),
) -> Preset:
    preset = await db.get(Preset, preset_id)
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")

    if body.name is not None:
        preset.name = body.name
    if body.description is not None:
        preset.description = body.description
    if body.config_json is not None:
        preset.config_json = [pedal.model_dump() for pedal in body.config_json]

    await db.flush()
    await db.refresh(preset)
    return preset


# -------------------------------------------------------------------
# DELETE /presets/{id}  – elimina preset
# -------------------------------------------------------------------
@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(preset_id: int, db: AsyncSession = Depends(get_db)) -> None:
    preset = await db.get(Preset, preset_id)
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    await db.delete(preset)
