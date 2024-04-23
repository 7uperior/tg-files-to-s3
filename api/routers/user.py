"""This module defines router for the api that is dedicated to user related responsibilities.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core import database, models, oauth2

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
def get_users(
    session: Session = Depends(database.get_session),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    users = database.get_all_users(session)

    return users
