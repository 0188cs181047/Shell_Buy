from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from core.security import (
    create_access_token, 
    create_refresh_token,
    verify_token
)
from model.user import User
from model.auth import Token, RefreshTokenRequest
from model import security, token
from database import get_session
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/auth/refresh", tags=["auth"])
SessionDep = Annotated[Session, Depends(get_session)]

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

@router.post("/", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: Request,
    session: SessionDep, 
    refresh_request: RefreshTokenRequest
):
    payload = verify_token(refresh_request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = session.get(User, user_id)
    if not user or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    account_security = session.exec(
        select(security.AccountSecurity).where(security.AccountSecurity.user_id == user.id)
    ).first()
    
    if not account_security or account_security.refresh_token != refresh_request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    if account_security.refresh_token_expires and account_security.refresh_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    new_refresh_token_expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    account_security.refresh_token = new_refresh_token
    account_security.refresh_token_expires = new_refresh_token_expires
    account_security.refresh_token_created_at = datetime.utcnow()
    account_security.refresh_token_ip = request.client.host
    account_security.refresh_token_user_agent = request.headers.get("user-agent")
    
    new_refresh_token_record = token.RefreshToken(
        token=new_refresh_token,
        user_id=user.id,
        expires_at=new_refresh_token_expires,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    session.add(new_refresh_token_record)
    
    old_refresh_token_record = session.exec(
        select(token.RefreshToken).where(token.RefreshToken.token == refresh_request.refresh_token)
    ).first()
    if old_refresh_token_record:
        old_refresh_token_record.revoked_at = datetime.utcnow()
    
    session.commit()
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )