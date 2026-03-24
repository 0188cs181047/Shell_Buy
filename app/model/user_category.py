from sqlmodel import Field, Relationship
from typing import Optional, List
from .base import CommonBaseModel
from sqlmodel import SQLModel, Field

class UserCategory(CommonBaseModel, table=True):
    __tablename__ = "user_categories"

    name: str = Field(index=True, unique=True, max_length=100)

    access_level_start: int
    access_level_end: int

    # Relationship (One category → Many users)
    users: List["User"] = Relationship(back_populates="category")


class UserCategoryCreate(SQLModel):
    name: str = Field(max_length=100)
    access_level_start: int
    access_level_end: int

class UserCategoryResponse(SQLModel):
    id: Optional[str]
    name: str
    access_level_start: int
    access_level_end: int