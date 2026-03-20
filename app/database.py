"""
database.py - Configurazione engine SQLAlchemy async (aiosqlite) e sessioni.
"""
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# -------------------------------------------------------------------
# Percorso del file SQLite
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # root del progetto
DB_DIR = BASE_DIR / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{DB_DIR / 'gtr_hub.db'}"

# -------------------------------------------------------------------
# Engine asincrono
# -------------------------------------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=True,          # log SQL in sviluppo – metti False in prod
    future=True,
)

# -------------------------------------------------------------------
# Session factory
# -------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# -------------------------------------------------------------------
# Base per i modelli ORM
# -------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# -------------------------------------------------------------------
# Dipendenza FastAPI – inietta una sessione per request
# -------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
