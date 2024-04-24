from sqlalchemy.exc import IntegrityError

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core import database, models, oauth2
from ..core.models import Transaction  

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=models.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_create: models.UserCreate, session: Session = Depends(database.get_session)):
    user_exists = database.get_user(user_create.email, session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {user_create.email} already exists",
        )
    else:
        user_create.password = oauth2.hash_password(user_create.password)
        user = database.add_user(user_create, session)
        return user

@router.get("/", response_model=List[models.UserRead])

def get_users(session: Session = Depends(database.get_session)): #, current_user: models.User = Depends(oauth2.get_current_user)):
    users = database.get_all_users(session)
    return users

@router.post("/create_via_tgid", response_model=models.UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_via_tgid(user_data: models.UserTelegramCreate, session: Session = Depends(database.get_session)):
    # Check if user already exists by both email and Telegram ID
    email = f"{user_data.telegram_id}@telegram.com"
    user_exists_by_email = database.get_user(email, session)
    user_exists_by_tgid = database.get_user_by_telegram_id(user_data.telegram_id, session)
    
    if user_exists_by_email or user_exists_by_tgid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with this email or Telegram ID already exists"
        )
    
    # Create a new user
    try:
        password = "default_password"  # Use a secure method for generating passwords in production
        hashed_password = oauth2.hash_password(password)
        # Include the telegram_id in the user creation data
        user_create = models.UserCreate(email=email, password=hashed_password, telegram_id=user_data.telegram_id)
        user = database.add_user(user_create, session)

        # Top-up initial credits
        initial_credit = 10
        transaction = Transaction(user_id=user.id, amount=initial_credit, transaction_type="top-up")
        session.add(transaction)
        session.commit()
        
        return user
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database integrity error, possibly duplicate data."
        )