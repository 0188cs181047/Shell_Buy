from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from .base import CommonBaseModel

class LoginHistory(CommonBaseModel, table=True):
    __tablename__ = "login_history"
    
    user_id: str = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=255)
    success: bool = Field(default=False)
    failure_reason: Optional[str] = Field(default=None, max_length=100)
    login_time: datetime = Field(default_factory=datetime.utcnow)
