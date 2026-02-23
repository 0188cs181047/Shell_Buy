from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime
from .base import CommonBaseModel

class RefreshToken(CommonBaseModel, table=True):
    __tablename__ = "refresh_tokens"
    
    token: str = Field(index=True, unique=True, max_length=500)
    user_id: str = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    expires_at: datetime
    revoked_at: Optional[datetime] = Field(default=None)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=255)