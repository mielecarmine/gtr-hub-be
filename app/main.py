"""
main.py - Entry point dell'applicazione FastAPI.

Avvio:
    uv run uvicorn app.main:app --reload --port 8000
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from app.database import Base, engine, get_db, AsyncSessionLocal

# Importa esplicitamente i moduli/router di feature
from app.users.router import router as users_router
from app.presets.router import router as presets_router

# Assicura che i modelli vengano importati prima di Base.metadata.create_all
# in modo che SQLAlchemy possa registrarli correttamente all'avvio.
from app.users.models import User
from app.presets.models import Preset


# -------------------------------------------------------------------
# Lifespan: crea le tabelle all'avvio (dev-friendly, usa Alembic in prod)
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Crea un utente di test con id=1 se non esiste già
    async with AsyncSessionLocal() as session:
        async with session.begin():
            test_user = await session.get(User, 1)
            if not test_user:
                user = User(
                    id=1,
                    username="testuser",
                    email="testuser@example.com",
                    hashed_password="hashed_testpassword",
                )
                session.add(user)
    yield
    # Cleanup (opzionale in dev)
    await engine.dispose()


# -------------------------------------------------------------------
# App instance
# -------------------------------------------------------------------
app = FastAPI(
    title="GTR Hub API",
    description="Backend per il simulatore web di amplificatori e effetti chitarra.",
    version="0.1.0",
    lifespan=lifespan,
)


# -------------------------------------------------------------------
# CORS middleware
# -------------------------------------------------------------------
ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Vite dev server (frontend)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Routers
# -------------------------------------------------------------------
app.include_router(users_router, prefix="/api/v1")
app.include_router(presets_router, prefix="/api/v1")


# -------------------------------------------------------------------
# Health-check
# -------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    return {"status": "ok", "message": "GTR Hub API is running 🎸"}


@app.get("/health", tags=["Health"])
async def health(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    try:
        # Test the database connection
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    status_code = "ok" if db_status == "healthy" else "error"
    return {
        "status": status_code,
        "database": db_status,
        "message": "GTR Hub API is running smoothly 🎸" if status_code == "ok" else "GTR Hub API has issues ⚠️"
    }
