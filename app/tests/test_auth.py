import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Register
        response = await ac.post("/api/v1/auth/register", json={
            "username": "testuser1",
            "email": "testuser1@example.com",
            "password": "securepassword123"
        })
        assert response.status_code == 201
        
        # Login
        response = await ac.post("/api/v1/auth/login", data={
            "username": "testuser1",
            "password": "securepassword123"
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        assert token is not None

        # Get me
        response = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["username"] == "testuser1"

@pytest.mark.asyncio
async def test_protected_presets():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/presets/")
        assert response.status_code == 401
