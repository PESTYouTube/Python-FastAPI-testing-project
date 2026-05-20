from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from core.auth import decode_access_token, extract_token
from crud import get_user_by_id
from db.session import get_db
from models.models import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    if getattr(request.state, "user", None) is not None:
        user = request.state.user
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account deactivated")
        return user

    token = extract_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account deactivated")

    request.state.user = user
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
