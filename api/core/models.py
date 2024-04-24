from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr, validator
from pydantic import Field as PydanticField
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
    
class FilesPricing(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    price_per_minute: float = Field()
    price_per_size: float = Field()  # price per MB
    extra_buffer_percentage: int = Field()


class FilesPricingCreate(BaseModel):
    price_per_minute: float = PydanticField(..., example=1.50)
    price_per_size: float = PydanticField(..., example=0.25)
    extra_buffer_percentage: int = PydanticField(..., example=10)

    @validator('price_per_minute', 'price_per_size', 'extra_buffer_percentage')
    def check_values_greater_than_zero(cls, v):
        if v <= 0:
            raise ValueError("must be greater than zero")
        return v