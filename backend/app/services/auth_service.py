import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.repository.user_repo import UserRepository
from app.schemas.auth import TokenPair, UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: UserCreate):
        if self.repo.get_by_email(data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
        role = "admin" if data.email.lower() == settings.admin_email.lower() else "user"
        return self.repo.add(
            email=data.email.lower(), full_name=data.full_name,
            hashed_password=hash_password(data.password), role=role,
        )

    @staticmethod
    def _pair(user) -> TokenPair:
        return TokenPair(access_token=create_token(user.id, user.role), refresh_token=create_token(user.id, user.role, "refresh"))

    def login(self, email: str, password: str) -> TokenPair:
        user = self.repo.get_by_email(email)
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
        return self._pair(user)

    def refresh(self, token: str) -> TokenPair:
        try:
            payload = decode_token(token)
        except jwt.PyJWTError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
        user = self.repo.get(int(payload["sub"])) if payload.get("type") == "refresh" else None
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
        return self._pair(user)
