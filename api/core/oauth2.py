"""This module is concerned with authentication and security related operations.
"""
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from . import database, models
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    """creates a JWT token that will later be used by users to authenticate their requests"""
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minute)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception: HTTPException):
    """verifies a JWT token has been encrypted using the applications secret key,
    has the expected data in the payload, and hasn't expired yet.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        _id = payload.get("user")
        if _id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return _id


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(database.get_session),
):
    """Gets a current user by verifying the JWT token passed, and using its payload data
    to query the users database for a corresponding  user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    _id = verify_access_token(token, credentials_exception)

    user = session.exec(select(models.User).where(models.User.id == _id)).first()

    return user


def hash_password(password: str) -> str:
    """hashes plain text password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verify plaintext password against hashed password in database"""
    return pwd_context.verify(plain_password, hashed_password)
