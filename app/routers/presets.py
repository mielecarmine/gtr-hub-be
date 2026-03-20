"""
routers/presets.py - Endpoint CRUD per i Preset.
"""
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Preset
from app.schemas import PresetCreate, PresetRead, PresetUpdate

router = APIRouter(prefix="/presets", tags=["Presets"])


# -------------------------------------------------------------------
# GET /presets  – lista tutti i preset (filtrabili per author_id)
# -------------------------------------------------------------------
@router.get("/", response_model=list[PresetRead])
async def list_presets(
    author_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Preset)
    if author_id is not None:
        stmt = stmt.where(Preset.author_id == author_id)
    result = await db.execute(stmt)
    presets = result.scalars().all()
    return [PresetRead.from_orm_preset(p) for p in presets]


# -------------------------------------------------------------------
# GET /presets/{id}  – singolo preset
# -------------------------------------------------------------------
@router.get("/{preset_id}", response_model=PresetRead)
async def get_preset(preset_id: int, db: AsyncSession = Depends(get_db)):
    preset = await db.get(Preset, preset_id)
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    return PresetRead.from_orm_preset(preset)


# -------------------------------------------------------------------
# POST /presets  – crea un nuovo preset
# -------------------------------------------------------------------
@router.post("/", response_model=PresetRead, status_code=status.HTTP_201_CREATED)
async def create_preset(
    body: PresetCreate,
    author_id: int,          # in futuro sostituire con JWT dependency
    db: AsyncSession = Depends(get_db),
):
    config_json = json.dumps([node.model_dump() for node in body.chain])
    preset = Preset(name=body.name, author_id=author_id, config=config_json)
    db.add(preset)
    await db.flush()   # ottiene l'id prima del commit
    await db.refresh(preset)
    return PresetRead.from_orm_preset(preset)


# -------------------------------------------------------------------
# PATCH /presets/{id}  – aggiornamento parziale
# -------------------------------------------------------------------
@router.patch("/{preset_id}", response_model=PresetRead)
async def update_preset(
    preset_id: int,
    body: PresetUpdate,
    db: AsyncSession = Depends(get_db),
):
    preset = await db.get(Preset, preset_id)
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")

    if body.name is not None:
        preset.name = body.name
    if body.chain is not None:
        preset.config = json.dumps([node.model_dump() for node in body.chain])

    await db.flush()
    await db.refresh(preset)
    return PresetRead.from_orm_preset(preset)


# -------------------------------------------------------------------
# DELETE /presets/{id}  – elimina preset
# -------------------------------------------------------------------
@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(preset_id: int, db: AsyncSession = Depends(get_db)):
    preset = await db.get(Preset, preset_id)
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    await db.delete(preset)
