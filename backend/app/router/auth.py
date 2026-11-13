from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.router.deps import current_user
from app.schemas.auth import RefreshIn, TokenPair, UserCreate, UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return AuthService(db).register(data)


@router.post("/login", response_model=TokenPair)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return AuthService(db).login(form.username, form.password)  # form.username carries the email


@router.post("/refresh", response_model=TokenPair)
def refresh(body: RefreshIn, db: Session = Depends(get_db)):
    return AuthService(db).refresh(body.refresh_token)


@router.get("/me", response_model=UserOut)
def me(user=Depends(current_user)):
    return user
