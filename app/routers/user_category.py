from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Annotated, List

from database import get_session
from model.user_category import UserCategory, UserCategoryCreate, UserCategoryResponse
from model.user import User
from core.security import get_current_user


router = APIRouter(prefix="/user-category", tags=["User Category"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/", response_model=UserCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_in: UserCategoryCreate, session: SessionDep, current_user: User = Depends(get_current_user)):

    existing = session.exec(
        select(UserCategory).where(UserCategory.name == category_in.name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    category = UserCategory(**category_in.model_dump())

    session.add(category)
    session.commit()
    session.refresh(category)

    return category

@router.get("/", response_model=List[UserCategoryResponse])
def get_all_categories(session: SessionDep, current_user: User = Depends(get_current_user)):
    
    categories = session.exec(select(UserCategory)).all()
    return categories

@router.get("/{category_id}", response_model=UserCategoryResponse)
def get_category(category_id: str, session: SessionDep, current_user: User = Depends(get_current_user)):
    
    category = session.get(UserCategory, category_id)

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category

@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(category_id: str, session: SessionDep, current_user: User = Depends(get_current_user)):
    
    category = session.get(UserCategory, category_id)

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    session.delete(category)
    session.commit()

    return {"message": "Category deleted successfully"}