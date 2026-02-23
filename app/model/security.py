from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from .base import CommonBaseModel

class AccountSecurity(CommonBaseModel, table=True):
    __tablename__ = "account_security"
    
    user_id: str = Field(foreign_key="users.id", unique=True, index=True, ondelete="CASCADE")
    
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    
    last_login: Optional[datetime] = Field(default=None)
    last_login_ip: Optional[str] = Field(default=None, max_length=45)
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)
    
    refresh_token: Optional[str] = Field(default=None, max_length=500) 
    refresh_token_expires: Optional[datetime] = Field(default=None) 
    refresh_token_created_at: Optional[datetime] = Field(default=None)
    refresh_token_ip: Optional[str] = Field(default=None, max_length=45) 
    refresh_token_user_agent: Optional[str] = Field(default=None, max_length=255)
    
    password_reset_token: Optional[str] = Field(default=None, max_length=255)
    password_reset_expires: Optional[datetime] = Field(default=None)
    
    email_verification_token: Optional[str] = Field(default=None, max_length=255)
    email_verified_at: Optional[datetime] = Field(default=None)