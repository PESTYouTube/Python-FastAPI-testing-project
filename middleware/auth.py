from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from core.auth import decode_access_token, extract_token
from crud import get_user_by_id
from db.session import SessionLocal


class AuthMiddleware(BaseHTTPMiddleware):
    """Определяет пользователя из JWT (Cookie или Authorization: Bearer)."""

    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        token = extract_token(request)
        if token:
            user_id = decode_access_token(token)
            if user_id:
                db = SessionLocal()
                try:
                    user = get_user_by_id(db, user_id)
                    if user and user.is_active:
                        request.state.user = user
                finally:
                    db.close()

        return await call_next(request)
