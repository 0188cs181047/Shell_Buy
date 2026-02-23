from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class CommonBaseModel(SQLModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )