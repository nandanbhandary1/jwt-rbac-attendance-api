from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .auth import decode_token
from .models import User

security = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    return user

def require_roles(allowed_roles: list):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return role_checker

def get_monitoring_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or payload.get("type") != "monitoring":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid monitoring token")
        
    user_id = payload.get("user_id")
    role = payload.get("role")
    
    if role != "monitoring_officer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not issued for monitoring officer")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "monitoring_officer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
        
    return user
