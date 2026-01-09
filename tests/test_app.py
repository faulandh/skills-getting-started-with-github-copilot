import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app


@pytest.mark.asyncio
async def test_get_activities():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/activities")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data


@pytest.mark.asyncio
async def test_signup_and_unregister():
    activity = "Chess Club"
    email = "tester@example.com"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Ensure clean state: remove test email if present
        r = await ac.get("/activities")
        participants = r.json()[activity]["participants"]
        if email in participants:
            await ac.delete(f"/activities/{activity}/participants", params={"email": email})

        # Sign up
        r = await ac.post(f"/activities/{activity}/signup", params={"email": email})
        assert r.status_code == 200
        assert "Signed up" in r.json().get("message", "")

        # Verify present
        r = await ac.get("/activities")
        assert email in r.json()[activity]["participants"]

        # Unregister
        r = await ac.delete(f"/activities/{activity}/participants", params={"email": email})
        assert r.status_code == 200
        assert "Unregistered" in r.json().get("message", "")

        # Verify removed
        r = await ac.get("/activities")
        assert email not in r.json()[activity]["participants"]
