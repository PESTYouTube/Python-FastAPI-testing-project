from enum import Enum

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from db.session import get_db
from models.models import AccessRoleRule, BusinessElement, User


class PermissionAction(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


def _is_admin(user: User) -> bool:
    return any(role.name == "admin" for role in user.roles)


def _get_rule(db: Session, role_id: str, element_id: str) -> AccessRoleRule | None:
    return (
        db.query(AccessRoleRule)
        .filter(
            AccessRoleRule.role_id == role_id,
            AccessRoleRule.element_id == element_id,
        )
        .first()
    )


def user_has_permission(
    db: Session,
    user: User,
    element_name: str,
    action: PermissionAction,
    owner_id: str | None = None,
) -> bool:
    if _is_admin(user):
        return True

    element = db.query(BusinessElement).filter(BusinessElement.name == element_name).first()
    if not element:
        return False

    for role in user.roles:
        rule = _get_rule(db, role.id, element.id)
        if not rule:
            continue

        if action == PermissionAction.READ:
            if rule.read_all_permission:
                return True
            if rule.read_permission and owner_id is not None and str(owner_id) == str(user.id):
                return True
            if rule.read_permission and owner_id is None:
                return True
        elif action == PermissionAction.CREATE and rule.create_permission:
            return True
        elif action == PermissionAction.UPDATE:
            if rule.update_all_permission:
                return True
            if rule.update_permission and owner_id is not None and str(owner_id) == str(user.id):
                return True
        elif action == PermissionAction.DELETE:
            if rule.delete_all_permission:
                return True
            if rule.delete_permission and owner_id is not None and str(owner_id) == str(user.id):
                return True

    return False


def can_list_resources(db: Session, user: User, element_name: str) -> tuple[bool, bool]:
    """Возвращает (доступ_есть, видит_все_объекты)."""
    if _is_admin(user):
        return True, True

    element = db.query(BusinessElement).filter(BusinessElement.name == element_name).first()
    if not element:
        return False, False

    see_all = False
    see_own = False
    for role in user.roles:
        rule = _get_rule(db, role.id, element.id)
        if not rule:
            continue
        if rule.read_all_permission:
            see_all = True
        if rule.read_permission:
            see_own = True

    return see_all or see_own, see_all


def require_permission(element_name: str, action: PermissionAction):
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if not user_has_permission(db, current_user, element_name, action):
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: {action.value} access to '{element_name}'",
            )
        return current_user

    return dependency
