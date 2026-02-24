from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from core.security import hash_password
from model.user import User, UserCreate, UserResponse
from model import security
from database import get_session
from services.send_email import send_register_email

router = APIRouter(prefix="/auth/register", tags=["auth"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(*, session: SessionDep, user_in: UserCreate, background_tasks: BackgroundTasks):
    existing_user = session.exec(
        select(User).where(User.email == user_in.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        name=user_in.name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        password=hash_password(user_in.password),
        is_active=True 
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)

    account_security = security.AccountSecurity(
        user_id=user.id,
        is_active=True,
        is_verified=False,
        is_superuser=False,
        failed_login_attempts=0
    )

    session.add(account_security)
    session.commit()

    background_tasks.add_task(
        send_register_email,
        user.email,
        user.name
    )

    return user