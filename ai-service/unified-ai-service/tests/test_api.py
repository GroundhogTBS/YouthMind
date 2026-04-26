import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import asyncio

from main import app


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoints:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "YouthMind AI Service"
        assert data["version"] == "1.0.0"

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_ready(self, client):
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestEmotionEndpoints:
    def test_analyze_emotion(self, client):
        response = client.post(
            "/ai/emotion/analyze",
            json={"text": "我今天很开心"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "primary_emotion" in data
        assert "confidence" in data

    def test_analyze_negative_emotion(self, client):
        response = client.post(
            "/ai/emotion/analyze",
            json={"text": "我很焦虑，考试压力很大"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["primary_emotion"] in ["anxious", "sad", "fear"]

    def test_get_supported_emotions(self, client):
        response = client.get("/ai/emotion/supported")
        assert response.status_code == 200
        data = response.json()
        assert "emotions" in data
        assert data["count"] > 0

    def test_get_keywords(self, client):
        response = client.get("/ai/emotion/keywords")
        assert response.status_code == 200
        data = response.json()
        assert "keywords" in data


class TestCrisisEndpoints:
    def test_detect_green(self, client):
        response = client.post(
            "/ai/crisis/detect",
            json={"text": "今天天气不错，心情也很好"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "green"

    def test_detect_yellow(self, client):
        response = client.post(
            "/ai/crisis/detect",
            json={"text": "最近学习压力很大，很焦虑"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ["yellow", "green"]

    def test_detect_red(self, client):
        response = client.post(
            "/ai/crisis/detect",
            json={"text": "我不想活了，想自杀"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "red"
        assert data["should_alert"] == True

    def test_get_resources(self, client):
        response = client.get("/ai/crisis/resources")
        assert response.status_code == 200
        data = response.json()
        assert "resources" in data
        assert data["count"] > 0

    def test_get_risk_levels(self, client):
        response = client.get("/ai/crisis/risk-levels")
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data


class TestChatEndpoints:
    def test_create_session(self, client):
        response = client.post(
            "/ai/chat/session",
            json={"title": "测试对话"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["title"] == "测试对话"

    def test_get_sessions(self, client):
        response = client.get("/ai/chat/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_send_message(self, client):
        session_response = client.post("/ai/chat/session")
        session_id = session_response.json()["session_id"]
        
        response = client.post(
            "/ai/chat/send",
            json={
                "session_id": session_id,
                "content": "你好，我想聊聊"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "emotion" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
