from functools import partial
from typing import Dict, List

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from api.core import models
from api.core.config import settings
from api.core.database import get_session
from api.core.queue import get_publisher
from api.main import app


@pytest.fixture
def session():
    DB_URL = f"postgresql://{settings.db_user}:{settings.db_password}@localhost:{settings.db_port}/{settings.db_name}"

    test_engine = create_engine(f"{DB_URL}")

    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_publisher] = partial(get_publisher, "files_test")

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def users(session: Session, client: TestClient):
    user_dicts: List[Dict[str, str]] = [
        {"email": "user1@email.com", "password": "123"},
        {"email": "user2@email.com", "password": "456"},
        {"email": "user3@email.com", "password": "789"},
    ]

    for user_dict in user_dicts:
        client.post("/users/", json=user_dict)
    user_models: List[models.UserCreate] = [
        models.UserCreate(**user) for user in user_dicts
    ]  # type: ignore

    yield user_models
    for user_model in user_models:
        statement = select(models.User).where(models.User.email == user_model.email)
        results = session.exec(statement)
        user = results.one()
        session.delete(user)
    session.commit()


@pytest.fixture
def logged_in_user(client: TestClient, users: List[models.UserCreate]):
    user_dict = {"email": "user1@email.com", "password": "123"}
    client.post("/users", json=user_dict)

    user_dict["username"] = user_dict.pop("email")
    response = client.post("/login", data=user_dict)

    yield response.json(), users
