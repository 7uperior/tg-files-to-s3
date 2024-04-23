import datetime
import logging

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse

from ..core import files, models, oauth2, queue

router = APIRouter(prefix='/files', tags=['Files'])

logger = logging.getLogger(__name__)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def upload_file(
	file: UploadFile,
	current_user: models.User = Depends(oauth2.get_current_user),
	client: files.Minio = Depends(files.get_minio_client),
	message_publisher: queue.Awaitable = Depends(queue.get_publisher),
):
	if not file.content_type.startswith('audio/'):
		return JSONResponse(
			status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
			content={'detail': 'Unsupported media type. Only audio files are accepted.'},
		)

	try:
		file_data = await file.read()  # Ensure file data is read asynchronously
		file_size = len(file_data)  # Get the file size from the data length
		object_name = f'{current_user.id}/{file.filename}'

		# Upload the file to Minio asynchronously using the helper function
		await files.upload_file_to_minio(client, files.BUCKET, object_name, file_data, file_size)

		return {
			'filename': file.filename,
			'content_type': file.content_type,
			'size': file_size,
			'date': datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
		}
	except Exception:
		logger.exception('Failed to upload file')
		return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'detail': 'Internal Server Error'})
