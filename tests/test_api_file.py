import tempfile
from typing import List, Tuple

from fastapi.testclient import TestClient

from api.core import models
from api.main import app

client = TestClient(app)


def test_upload_audio_file_success(client: TestClient, logged_in_user: Tuple[dict, List[models.UserCreate]]):
	jwt = logged_in_user[0]['access_token']
	headers = {'Authorization': f'Bearer {jwt}'}

	# Simulating audio file upload
	with tempfile.NamedTemporaryFile(suffix='.mp3') as fp:
		fp.write(b'Fake audio data')
		fp.seek(0)
		files = [('file', ('test_audio.mp3', fp, 'audio/mpeg'))]
		response = client.post('/files/', headers=headers, files=files)

		data = response.json()
		assert response.status_code == 201
		assert data['filename'] == 'test_audio.mp3'
		assert data['content_type'] == 'audio/mpeg'
		assert 'size' in data  # Ensuring size is reported
		assert 'date' in data  # Ensuring date is reported


def test_upload_unsupported_file_type(client: TestClient, logged_in_user: Tuple[dict, List[models.UserCreate]]):
	jwt = logged_in_user[0]['access_token']
	headers = {'Authorization': f'Bearer {jwt}'}

	# Simulating wrong file type upload
	with tempfile.NamedTemporaryFile(suffix='.txt') as fp:
		fp.write(b'This is a text file, not an audio file.')
		fp.seek(0)
		files = [('file', ('not_audio.txt', fp, 'text/plain'))]
		response = client.post('/files/', headers=headers, files=files)

		assert response.status_code == 415
		assert 'Unsupported media type' in response.json()['detail']


def test_upload_file_auth_fail(client: TestClient):
	# Test upload without authentication
	with tempfile.NamedTemporaryFile(suffix='.mp3') as fp:
		fp.write(b'Some audio data')
		fp.seek(0)
		files = [('file', ('audio.mp3', fp, 'audio/mpeg'))]
		response = client.post('/files/', files=files)

		assert response.status_code == 401
		assert 'detail' in response.json()
		assert response.json()['detail'] == 'Not authenticated'
