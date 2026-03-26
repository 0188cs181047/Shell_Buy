from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
import os
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.database import get_session
from app.model.user import User
from fastapi import HTTPException, status, Depends

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new access token"""
    to_encode = data.copy()
    
    # Set expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc)
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        print(f"Error creating access token: {e}")
        raise

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a new refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.now(timezone.utc)
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        print(f"Error creating refresh token: {e}")
        raise

def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify a token and return payload if valid"""
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            print(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error verifying token: {e}")
        return None

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_current_user(token: str = Depends(oauth2_scheme),session: Session = Depends(get_session)):
    payload = verify_token(token, token_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user
