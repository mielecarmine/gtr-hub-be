"""
presets/router.py - Endpoint CRUD per i Preset.
"""
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.presets.models import Preset
from app.presets.schemas import PresetCreate, PresetOut, PresetUpdate
from app.auth.dependencies import get_current_user
from app.users.models import User

router = APIRouter(prefix="/presets", tags=["Presets"])


# -------------------------------------------------------------------
# GET /presets  – lista tutti i preset dell'utente corrente
# -------------------------------------------------------------------
@router.get("/", response_model=list[PresetOut])
async def list_presets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Sequence[Preset]:
    stmt = select(Preset).where(Preset.user_id == current_user.id)
    result = await db.execute(stmt)
    presets = result.scalars().all()
    return presets


# -------------------------------------------------------------------
# GET /presets/{id}  – singolo preset
# -------------------------------------------------------------------
@router.get("/{preset_id}", response_model=PresetOut)
async def get_preset(
    preset_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Preset:
    preset = await db.get(Preset, preset_id)
    if preset is None or preset.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    return preset


# -------------------------------------------------------------------
# POST /presets  – crea un nuovo preset
# -------------------------------------------------------------------
@router.post("/", response_model=PresetOut, status_code=status.HTTP_201_CREATED)
async def create_preset(
    body: PresetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Preset:
    if body.client_id:
        stmt = select(Preset).where(
            Preset.client_id == body.client_id,
            Preset.user_id == current_user.id
        )
        result = await db.execute(stmt)
        existing_preset = result.scalars().first()
        if existing_preset:
            return existing_preset

    preset = Preset(
        name=body.name,
        description=body.description,
        user_id=current_user.id,
        client_id=body.client_id,
        config_json=[pedal.model_dump() for pedal in body.effects_chain],
    )
    try:
        db.add(preset)
        await db.flush()
        await db.refresh(preset)
        return preset
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error during preset creation: {str(e)}",
        )


# -------------------------------------------------------------------
# PATCH /presets/{id}  – aggiornamento parziale
# -------------------------------------------------------------------
@router.patch("/{preset_id}", response_model=PresetOut)
async def update_preset(
    preset_id: int,
    body: PresetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Preset:
    preset = await db.get(Preset, preset_id)
    if preset is None or preset.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")

    if body.name is not None:
        preset.name = body.name
    if body.description is not None:
        preset.description = body.description
    if body.effects_chain is not None:
        preset.config_json = [pedal.model_dump() for pedal in body.effects_chain]

    await db.flush()
    await db.refresh(preset)
    return preset


# -------------------------------------------------------------------
# DELETE /presets/{id}  – elimina preset
# -------------------------------------------------------------------
@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(
    preset_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    preset = await db.get(Preset, preset_id)
    if preset is None or preset.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    await db.delete(preset)
