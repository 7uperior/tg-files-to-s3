from typing import List, Tuple

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from api.core import models


def test_create_user(session: Session, client: TestClient):
    payload = {"email": "user@email.com", "password": "password"}

    response = client.post("/users/", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["email"] == "user@email.com"

    statement = select(models.User).where(models.User.email == "user@email.com")
    results = session.exec(statement)
    hero = results.one()
    session.delete(hero)
    session.commit()


def test_duplicate_create_user_fail(session: Session, client: TestClient):
    payload = {"email": "user@email.com", "password": "password"}
    response = client.post("/users/", json=payload)

    # client twice to attempt creating a duplicate user based on email
    response = client.post("/users/", json=payload)

    assert response.status_code == 409

    statement = select(models.User).where(models.User.email == "user@email.com")
    results = session.exec(statement)
    hero = results.one()
    session.delete(hero)
    session.commit()


def test_read_users(client: TestClient, logged_in_user: Tuple[dict, List[models.UserCreate]]):

    jwt = logged_in_user[0]["access_token"]
    headers = {"Authorization": f"Bearer {jwt}"}
    response = client.get("/users", headers=headers)
    data = response.json()

    users = logged_in_user[1]
    assert len(data) == 3
    assert response.status_code == 200
    assert data[0]["email"] == users[0].email
    assert data[1]["email"] == users[1].email
    assert data[2]["email"] == users[2].email


def test_read_users_fail_auth(client: TestClient):
    response = client.get("/users")

    assert response.status_code == 401
