from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_create_item():
    res = client.post("/items", json={"name": "Caneta", "price": 2.5})
    assert res.status_code == 200
    assert res.json()["created"]["name"] == "Caneta"
