from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.model.user import User, UserResponse
from app.model import security
from app.database import get_session
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.get("/current_user/", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user(session: SessionDep, current_user: User = Depends(get_current_user)):
    try:
        statement = select(User).where(User.id == current_user.id)
        user = session.exec(statement).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: str = Depends(get_current_user), session: Session = Depends(get_session)):
    account_security = session.exec(
        select(security.AccountSecurity)
        .where(security.AccountSecurity.user_id == current_user.id)
    ).first()

    if account_security:
        account_security.refresh_token = None
        account_security.refresh_token_expires = None
    session.commit()
    
    return {"message": "Successfully logged out"}

@router.post("/delete_current_user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user: str = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        user = session.get(User, current_user.id)
        
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"User with id {current_user.id} not found"
            )
        
        session.delete(user)
        session.commit()
        
        return {
            "message": f"User with id {current_user.id} deleted successfully",
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