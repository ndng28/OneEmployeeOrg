import pytest
from httpx import AsyncClient, ASGITransport
from oneorg.api.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_login_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/login")
        assert response.status_code == 200
        assert "Sign In" in response.text

@pytest.mark.asyncio
async def test_register_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/register")
        assert response.status_code == 200
        assert "Join the Academy" in response.text

@pytest.mark.asyncio
async def test_root_redirects_to_login():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        response = await client.get("/")
        assert response.status_code == 200
        # After redirects, should be at login page
        assert "Sign In" in response.text
