import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models import User
from app.repository.user_repo import UserRepository

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    exc = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise exc
    user = UserRepository(db).get(int(payload["sub"])) if payload.get("type") == "access" else None
    if not user or not user.is_active:
        raise exc
    return user


def admin_only(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin role required")
    return user
