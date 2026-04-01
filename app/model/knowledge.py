from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid
from app.model.base import CommonBaseModel


class KnowledgeBase(CommonBaseModel, table=True):
    __tablename__ = "vector_db_knowledge"


    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # File info
    file_name: Optional[str] = Field(default=None)
    file_type: Optional[str] = Field(default=None)
    file_path: Optional[str] = Field(default=None)

    # Raw text (for small inputs or extracted content)
    content: Optional[str] = Field(default=None)

    # Metadata
    category: Optional[str] = Field(default="general")
    created_by: Optional[str] = Field(foreign_key="users.id")
