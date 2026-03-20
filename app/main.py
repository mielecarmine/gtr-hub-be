"""
main.py - Entry point dell'applicazione FastAPI.

Avvio:
    uv run uvicorn app.main:app --reload --port 8000
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import presets, users


# -------------------------------------------------------------------
# Lifespan: crea le tabelle all'avvio (dev-friendly, usa Alembic in prod)
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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
app.include_router(users.router, prefix="/api/v1")
app.include_router(presets.router, prefix="/api/v1")


# -------------------------------------------------------------------
# Health-check
# -------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "GTR Hub API is running 🎸"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
