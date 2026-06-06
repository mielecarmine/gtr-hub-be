import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    import uuid
    uid = uuid.uuid4().hex[:8]
    username = f"user_{uid}"
    email = f"user_{uid}@example.com"
    password = "securepassword123"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Register
        response = await ac.post("/api/v1/auth/register", json={
            "username": username,
            "email": email,
            "password": password
        })
        assert response.status_code == 201
        
        # Login
        response = await ac.post("/api/v1/auth/login", data={
            "username": username,
            "password": password
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        assert token is not None

        # Get me
        response = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["username"] == username

@pytest.mark.asyncio
async def test_protected_presets():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/presets/")
        assert response.status_code == 401
