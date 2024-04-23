from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")

    assert r.json() == {"message": "Hello World"}
    assert r.status_code == 200
