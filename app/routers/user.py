from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from typing import Annotated, List
from sqlmodel import Session, select
from app.core.security import hash_password

from app.database import get_session
from app.model.user import User, UserCreate, UserResponse, UserUpdate, AssignUserCategory
from app.model.security import AccountSecurity
from app.core.security import get_current_user
from app.services.send_email import send_category_assign_email
from app.model.user_category import UserCategory

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/add/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, session: SessionDep, current_user: User = Depends(get_current_user)):
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    try:
        user = User(
            name=user_data.name,
            email=user_data.email,
            phone_number=user_data.phone_number,
            password=hash_password(user_data.password)
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)

        account_security = AccountSecurity(
            user_id=user.id,
            is_active=True,
            is_verified=False,
            is_superuser=False,
            failed_login_attempts=0
        )

        session.add(account_security)
        session.commit()
        return user
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/details/", response_model=List[UserResponse],status_code=status.HTTP_200_OK)
def read_users(session: SessionDep, current_user: User = Depends(get_current_user), offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    try:
        statement = select(User).offset(offset).limit(limit)
        users = session.exec(statement).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detail/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def read_user(user_id: str, session: SessionDep, current_user: User = Depends(get_current_user)):
    try:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return user
    except Exception as e:
        print(f"Error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/edit/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: str, user_data: UserUpdate, session: SessionDep, current_user: User = Depends(get_current_user)):
    try:
        user = session.get(User, user_id)
        
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"User with id {user_id} not found"
            )
        
        if user_data.email != user.email:
            existing_user = session.exec(
                select(User).where(User.email == user_data.email)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=400, 
                    detail="User with this email already exists"
                )
        
        user.name = user_data.name
        user.email = user_data.email
        user.phone_number = user_data.phone_number
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating user: {str(e)}"
        )
    
@router.patch("/edit_partial/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user_partial(user_id: str, user_data: UserUpdate, session: SessionDep, current_user: User = Depends(get_current_user)):
    try:
        user = session.get(User, user_id)
        
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"User with id {user_id} not found"
            )
        
        update_data = user_data.model_dump(exclude_unset=True)
        if 'email' in update_data and update_data['email'] != user.email:
            existing_user = session.exec(
                select(User).where(User.email == update_data['email'])
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=400, 
                    detail="User with this email already exists"
                )
        
        for key, value in update_data.items():
            setattr(user, key, value)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating user: {str(e)}"
        )
    

@router.delete("/delete/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: str, session: SessionDep, current_user: User = Depends(get_current_user)):
    try:
        user = session.get(User, user_id)
        
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"User with id {user_id} not found"
            )
        
        session.delete(user)
        session.commit()
        
        return {
            "message": f"User with id {user_id} deleted successfully",
            "deleted_user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error deleting user: {str(e)}"
        )
    
@router.delete("/bulk-delete/", status_code=status.HTTP_200_OK)
def delete_users_bulk(user_ids: List[str], session: SessionDep, current_user: User = Depends(get_current_user)):
    try:
        deleted_users = []
        not_found = []
        
        for user_id in user_ids:
            user = session.get(User, user_id)
            if user:
                session.delete(user)
                deleted_users.append({"id": user_id, "name": user.name, "email": user.email})
            else:
                not_found.append(user_id)
        
        session.commit()
        
        return {
            "message": f"Successfully deleted {len(deleted_users)} users",
            "deleted_users": deleted_users,
            "not_found": not_found
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error deleting users: {str(e)}"
        )
    
@router.put("/{user_id}/assign-category", status_code=status.HTTP_200_OK)
def assign_user_category(
    user_id: str,
    data: AssignUserCategory,
    session: SessionDep,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    # Check user
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check category
    category = session.get(UserCategory, data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Assign category
    user.category_id = category.id
    session.add(user)
    session.commit()
    session.refresh(user)

    # Trigger email in background
    background_tasks.add_task(
        send_category_assign_email,
        user.email,
        user.name,
        category.name,
        category.access_level_start,
        category.access_level_end
    )

    return {
        "message": "Category assigned successfully & email sent",
        "user_id": user.id,
        "category": category.name
    }