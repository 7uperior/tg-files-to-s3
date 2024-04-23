import asyncio
import logging
import os
from io import BytesIO

from minio import Minio, S3Error

BUCKET = 'audio'

logger = logging.getLogger(__name__)


def get_minio_client() -> Minio:
	try:
		client = Minio(
			'minio:9000',
			access_key=os.getenv('MINIO_ROOT_USER'),
			secret_key=os.getenv('MINIO_ROOT_PASSWORD'),
			secure=False,  # Consider enabling TLS for production
		)

		# Check if the bucket exists and create it if it doesn't
		if not client.bucket_exists(BUCKET):
			client.make_bucket(BUCKET)

		return client
	except S3Error:
		logger.exception('An error occurred while setting up MinIO')
		raise


async def upload_file_to_minio(client: Minio, bucket: str, object_name: str, data: bytes, length: int):
	try:
		# Wrap the bytes data in a BytesIO object
		data_stream = BytesIO(data)
		await asyncio.to_thread(client.put_object, bucket, object_name, data_stream, length)
	except Exception:
		logger.exception('Failed to upload file to MinIO')
		raise
