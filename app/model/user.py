from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from .base import CommonBaseModel
from pydantic import validator

class User(CommonBaseModel, table=True):
    __tablename__ = "users"

    name: str = Field(index=True, max_length=255)
    email: str = Field(index=True, unique=True, max_length=255)
    phone_number: Optional[str] = Field(default=None, max_length=15)
    password: str
    category_id: Optional[int] = Field(default=None, foreign_key="user_categories.id")
    category: Optional["UserCategory"] = Relationship(back_populates="users")

class UserCreate(SQLModel):
    name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    phone_number: Optional[str] = Field(default=None, max_length=15)
    password: str
    
    @validator('password')
    def validate_password_length(cls, v):
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError(f'Password exceeds maximum length of 72 bytes (current: {len(password_bytes)} bytes)')
        return v

class UserUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    phone_number: Optional[str] = Field(default=None, max_length=15)

class UserCategoryResponse(SQLModel):
    id: Optional[str]
    name: str
    access_level_start: int
    access_level_end: int

class UserResponse(CommonBaseModel):
    name: str
    email: str
    phone_number: Optional[str] = None
    category: Optional[UserCategoryResponse] = None  

class UserLogin(SQLModel):
    email: str
    password: str

class AssignUserCategory(SQLModel):
    category_id: Optional[str]