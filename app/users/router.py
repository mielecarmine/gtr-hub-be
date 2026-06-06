"""
users/router.py - Endpoint per la gestione degli utenti.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.users.models import User
from app.users.schemas import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["Users"])


def _fake_hash(password: str) -> str:
    """Placeholder – sostituire con bcrypt/argon2 in produzione."""
    return f"hashed_{password}"


# -------------------------------------------------------------------
# POST /users  – registrazione utente
# -------------------------------------------------------------------
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    # Controllo username duplicato
    result = await db.execute(select(User).where(User.username == body.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=_fake_hash(body.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


# -------------------------------------------------------------------
# GET /users/{id}  – profilo utente
# -------------------------------------------------------------------
@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
