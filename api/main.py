from fastapi import FastAPI, Depends
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from .core import database
from .core.models import User, UserCreate
from .routers import auth, file, balance, transaction, user as user_router
from .core.oauth2 import hash_password  # Ensure this is correctly imported

app = FastAPI()

app.include_router(auth.router)
app.include_router(file.router)
app.include_router(user_router.router)
app.include_router(balance.router)
app.include_router(transaction.router)


@app.on_event("startup")
def on_startup():
    database.create_tables()  # Ensure tables are created

@app.get("/")
def root():
    return {"message": "Hello World"}