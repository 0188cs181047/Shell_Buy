from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core.security import (
    create_access_token, 
    create_refresh_token,
    verify_password,
)
from app.model.user import User
from app.model.auth import Token
from app.model import security, token
from app.model.login import LoginHistory
from app.database import get_session
from datetime import datetime, timedelta
import os

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

router = APIRouter(prefix="/auth/login", tags=["auth"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    request: Request, 
    session: SessionDep, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first() or session.exec(
        select(User).where(User.name == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    account_security = session.exec(
        select(security.AccountSecurity).where(security.AccountSecurity.user_id == user.id)
    ).first()
    
    if account_security and account_security.locked_until:
        if account_security.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is locked. Please try again later.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    refresh_token_expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    if not account_security:
        account_security = security.AccountSecurity(
            user_id=user.id,
            last_login=datetime.utcnow(),
            last_login_ip=ip_address,
            failed_login_attempts=0,
            refresh_token=refresh_token,
            refresh_token_expires=refresh_token_expires,
            refresh_token_created_at=datetime.utcnow(),
            refresh_token_ip=ip_address,
            refresh_token_user_agent=user_agent
        )
        session.add(account_security)
    else:
        account_security.last_login = datetime.utcnow()
        account_security.last_login_ip = ip_address
        account_security.failed_login_attempts = 0
        account_security.locked_until = None
        account_security.refresh_token = refresh_token
        account_security.refresh_token_expires = refresh_token_expires
        account_security.refresh_token_created_at = datetime.utcnow()
        account_security.refresh_token_ip = ip_address
        account_security.refresh_token_user_agent = user_agent
    
    refresh_token_record = token.RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=refresh_token_expires,
        ip_address=ip_address,
        user_agent=user_agent
    )
    session.add(refresh_token_record)
    
    login_history = LoginHistory(
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    session.add(login_history)
    
    session.commit()
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
