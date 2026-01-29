from datetime import datetime, timedelta
import hashlib
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, UserRole

# API Key header for token
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password


def create_access_token(email: str, role: str) -> str:
    """Create a JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": email, "role": role, "exp": expire}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    auth_header: str = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing token"
    )
    
    if not auth_header:
        raise credentials_exception
    
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else auth_header
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
