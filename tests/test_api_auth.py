from typing import List

from api.core import models
from fastapi.testclient import TestClient


def test_login_success(client: TestClient, users: List[models.UserCreate]):
	payload = {'username': users[0].email, 'password': users[0].password}
	response = client.post('/login', data=payload)
	data = response.json()

	assert response.status_code == 200
	assert 'access_token' in data
	assert data['token_type'] == 'bearer'


def test_login_email_fail(client: TestClient, users: List[models.UserCreate]):
	payload = {'username': 'wrong@email.com', 'password': users[0].password}

	response = client.post('/login', data=payload)

	assert response.status_code == 403


def test_login_password_fail(client: TestClient, users: List[models.UserCreate]):
	payload = {'username': users[0].email, 'password': 'wrong password'}

	response = client.post('/login', data=payload)

	assert response.status_code == 403
