from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr
from sqlmodel import Field, SQLModel, Relationship, Index

class UserBase(SQLModel):
    """Base model for user, capturing common fields."""
    email: EmailStr = Field(sa_column_kwargs={"index": True, "unique": True}, description="The user's email address, must be unique.")

class UserCreate(BaseModel):
    """User data required explicitly for creating a new user."""
    email: EmailStr
    password: str
    telegram_id: str


class UserTelegramCreate(BaseModel):
    """Model for creating a user via Telegram ID."""
    telegram_id: str

class User(UserBase, table=True):
    """User model representing an authenticated user in the system."""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: Optional[str] = Field(default=None, index=True, nullable=True, description="The user's Telegram ID.")
    password: str = Field(description="The user's hashed password.")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    transactions: List["Transaction"] = Relationship(back_populates="user")

class UserRead(UserBase):
    """Serialization model for reading user data."""
    id: int
    created_at: datetime

class UserLogin(UserCreate):
    """User login model, leveraging the same fields as UserCreate."""
    pass

class Token(SQLModel):
    """Model for JWT tokens used in authentication."""
    access_token: str = Field(description="JWT access token.")
    token_type: str = Field(default="Bearer", description="Token type, typically 'Bearer'.")

class Transaction(SQLModel, table=True):
    """Model representing financial transactions of a user."""
    __tablename__ = 'transactions'
    __table_args__ = (Index('idx_user_id', 'user_id'),)
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    amount: float = Field()
    transaction_type: constr(regex="^(top-up|reduction)$") = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user: User = Relationship(back_populates="transactions")
