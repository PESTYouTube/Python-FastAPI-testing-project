from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from core.auth import create_access_token
from core.config import get_settings
from core.dependencies import get_current_user
from crud import create_user, deactivate_user, get_user_by_email, verify_password
from db.session import get_db
from models.models import User
from schemas import UserLoginSchema, UserRegisterSchema

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register")
def register(credentials: UserRegisterSchema, db: Session = Depends(get_db)):
    if credentials.password != credentials.password_repeat:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if get_user_by_email(db, credentials.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(db, credentials)
    return {
        "message": "User created successfully",
        "email": user.email,
        "fullname": user.fullname,
    }


@router.post("/login")
def login(credentials: UserLoginSchema, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token(user.id)
    response.set_cookie(
        key=settings.JWT_ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response, current_user: User = Depends(get_current_user)):
    response.delete_cookie(settings.JWT_ACCESS_COOKIE_NAME)
    return {"message": "You have been logged out"}
