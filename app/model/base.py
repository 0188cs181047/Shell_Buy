from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from datetime import datetime
import uuid

class CommonBaseModel(SQLModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(String(36), primary_key=True, nullable=False),
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True),
                         server_default=func.now(),
                         nullable=False),
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True),
                         server_default=func.now(),
                         onupdate=func.now(),
                         nullable=False),
    )