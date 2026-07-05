import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_generate_rejects_wrong_prefix(client):
    r = await client.post("/generate-readme", json={"folder_path": "/tmp/foo"})
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_generate_rejects_nonexistent(client):
    r = await client.post("/generate-readme", json={"folder_path": "/Users/rudra/Documents/projects-github/nonexistent"})
    assert r.status_code == 400
