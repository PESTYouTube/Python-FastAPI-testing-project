from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from core.config import get_settings
from core.dependencies import get_current_user
from crud import deactivate_user, update_user, verify_password
from db.session import get_db
from models.models import User
from schemas import UserUpdateSchema

router = APIRouter(prefix="/users", tags=["users"])
settings = get_settings()


@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "surname": current_user.surname,
        "patronymic": current_user.patronymic,
        "fullname": current_user.fullname,
        "roles": [role.name for role in current_user.roles],
    }


@router.put("/me")
def update_my_profile(
    user_update: UserUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_update.password:
        if not user_update.old_password or not verify_password(
            user_update.old_password, current_user.hashed_password
        ):
            raise HTTPException(status_code=400, detail="Old password is incorrect")
        if user_update.password != user_update.password_repeat:
            raise HTTPException(status_code=400, detail="New passwords do not match")

    updated_user = update_user(db, current_user, user_update)
    return {
        "message": "User updated",
        "user": {
            "email": updated_user.email,
            "fullname": updated_user.fullname,
        },
    }


@router.delete("/me")
def delete_account(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deactivate_user(db, current_user)
    response.delete_cookie(settings.JWT_ACCESS_COOKIE_NAME)
    return {"message": "Account deactivated successfully"}
