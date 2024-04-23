import logging

from fastapi import Depends, FastAPI, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import get_db
from .models.file import File as ModelFile
from .models.user import User as ModelUser
from .schemas.file import File as SchemaFile
from .schemas.file import FileCreate

# Constants
AUDIO_FILE_CREATION_ERROR = 'Failed to create audio file.'
USER_NOT_FOUND_ERROR = 'User not found'
INSUFFICIENT_BALANCE_ERROR = 'Insufficient balance, please top up to continue'
FILE_PROCESSING_MESSAGE = 'Files queued for processing'
COST_PER_FILE = 10.0  # Example cost per file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.post('/audio_file_upload/', response_model=SchemaFile, status_code=status.HTTP_201_CREATED)
def create_audio_file(audio_file: FileCreate, db: Session = Depends(get_db)):
	try:
		db_audio_file = ModelFile(**audio_file.dict())
		db.add(db_audio_file)
		db.commit()
		db.refresh(db_audio_file)
		return db_audio_file
	except SQLAlchemyError as e:
		db.rollback()
		logger.error(f'Failed to create audio file: {e}', exc_info=True)
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=AUDIO_FILE_CREATION_ERROR) from e


@app.post('/upload-files/', status_code=status.HTTP_201_CREATED)
async def upload_files(files: list[UploadFile], user_id: int, db: Session = Depends(get_db)):
	user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_ERROR)

	total_cost = len(files) * COST_PER_FILE
	if user.balance < total_cost:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INSUFFICIENT_BALANCE_ERROR)

	for file in files:
		# Placeholder: Assume files are processed here or sent to a queue
		pass

	user.balance -= total_cost
	db.commit()

	return {'message': FILE_PROCESSING_MESSAGE, 'total_cost': total_cost}
