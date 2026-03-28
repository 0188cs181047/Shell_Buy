from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from app.core.security import hash_password
from app.model.user import User, UserCreate, UserResponse
from app.model import security
from app.database import get_session
from app.services.send_email import send_register_email
from app.model.user_category import UserCategory

router = APIRouter(prefix="/auth/register", tags=["auth"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(*, session: SessionDep, user_in: UserCreate, background_tasks: BackgroundTasks):
    
    # Check existing user
    existing_user = session.exec(
        select(User).where(User.email == user_in.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if "User" category exists
    user_category = session.exec(
        select(UserCategory).where(UserCategory.name == "User")
    ).first()

    # If not exists → create it
    if not user_category:
        user_category = UserCategory(
            name="User",
            access_level_start=10,
            access_level_end=15
        )
        session.add(user_category)
        session.commit()
        session.refresh(user_category)

    # Create user with category_id
    user = User(
        name=user_in.name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        password=hash_password(user_in.password),
        is_active=True,
        category_id=user_category.id   # 🔥 important
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)

    # Account security
    account_security = security.AccountSecurity(
        user_id=user.id,
        is_active=True,
        is_verified=False,
        is_superuser=False,
        failed_login_attempts=0
    )

    session.add(account_security)
    session.commit()

    # Send email
    background_tasks.add_task(
        send_register_email,
        user.email,
        user.name
    )
    return user