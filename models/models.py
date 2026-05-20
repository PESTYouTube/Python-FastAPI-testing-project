from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class BaseId(Base):
    __abstract__ = True
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()), index=True)


user_role = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


class User(BaseId):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    patronymic: Mapped[str | None] = mapped_column(nullable=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    roles: Mapped[list["Role"]] = relationship(secondary="user_roles", back_populates="users")

    @property
    def fullname(self) -> str:
        parts = [self.name, self.surname]
        if self.patronymic:
            parts.append(self.patronymic)
        return " ".join(parts)


class Role(BaseId):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(default="")

    users: Mapped[list[User]] = relationship(secondary="user_roles", back_populates="roles")
    access_rules: Mapped[list["AccessRoleRule"]] = relationship(back_populates="role")


class BusinessElement(BaseId):
    """Объекты приложения, к которым нужен доступ."""

    __tablename__ = "business_elements"

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)

    rules: Mapped[list["AccessRoleRule"]] = relationship(back_populates="element")


class AccessRoleRule(BaseId):
    """Правила доступа роли к бизнес-элементу (access_roles_rules)."""

    __tablename__ = "access_roles_rules"
    __table_args__ = (UniqueConstraint("role_id", "element_id", name="uq_role_element"),)

    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), nullable=False)
    element_id: Mapped[str] = mapped_column(ForeignKey("business_elements.id"), nullable=False)

    read_permission: Mapped[bool] = mapped_column(default=False)
    read_all_permission: Mapped[bool] = mapped_column(default=False)
    create_permission: Mapped[bool] = mapped_column(default=False)
    update_permission: Mapped[bool] = mapped_column(default=False)
    update_all_permission: Mapped[bool] = mapped_column(default=False)
    delete_permission: Mapped[bool] = mapped_column(default=False)
    delete_all_permission: Mapped[bool] = mapped_column(default=False)

    role: Mapped["Role"] = relationship(back_populates="access_rules")
    element: Mapped["BusinessElement"] = relationship(back_populates="rules")
