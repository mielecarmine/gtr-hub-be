"""
users/router.py - Endpoint per la gestione degli utenti.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.users.models import User
from app.users.schemas import UserOut

router = APIRouter(prefix="/users", tags=["Users"])


# -------------------------------------------------------------------
# GET /users/{id}  – profilo utente
# -------------------------------------------------------------------
@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
