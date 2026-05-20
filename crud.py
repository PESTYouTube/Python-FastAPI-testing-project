import bcrypt
from sqlalchemy.orm import Session, joinedload

import models.models
from schemas import UserRegisterSchema, UserUpdateSchema


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_user_by_email(db: Session, email: str) -> models.models.User | None:
    return db.query(models.models.User).filter(models.models.User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> models.models.User | None:
    return (
        db.query(models.models.User)
        .options(joinedload(models.models.User.roles))
        .filter(models.models.User.id == str(user_id))
        .first()
    )


def create_user(db: Session, data: UserRegisterSchema) -> models.models.User:
    db_user = models.models.User(
        email=data.email,
        name=data.name,
        surname=data.surname,
        patronymic=data.patronymic,
        hashed_password=get_password_hash(data.password),
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    default_role = db.query(models.models.Role).filter(models.models.Role.name == "user").first()
    if default_role:
        db_user.roles.append(default_role)
        db.commit()
        db.refresh(db_user)

    return db_user


def _get_user_in_session(db: Session, user_id: str) -> models.models.User:
    db_user = db.query(models.models.User).filter(models.models.User.id == user_id).first()
    if not db_user:
        raise ValueError("User not found")
    return db_user


def update_user(db: Session, user: models.models.User, data: UserUpdateSchema) -> models.models.User:
    user = _get_user_in_session(db, user.id)
    if data.email is not None:
        user.email = data.email
    if data.name is not None:
        user.name = data.name
    if data.surname is not None:
        user.surname = data.surname
    if data.patronymic is not None:
        user.patronymic = data.patronymic
    if data.password:
        user.hashed_password = get_password_hash(data.password)

    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user: models.models.User) -> None:
    db_user = _get_user_in_session(db, user.id)
    db_user.is_active = False
    db.commit()
