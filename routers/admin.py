from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from core.dependencies import require_admin
from db.session import get_db
from models.models import AccessRoleRule, BusinessElement, Role, User
from schemas import AccessRuleResponse, AccessRuleSchema, AccessRuleUpdateSchema

router = APIRouter(prefix="/admin/permissions", tags=["admin"])


def _serialize_rule(rule: AccessRoleRule) -> AccessRuleResponse:
    return AccessRuleResponse(
        id=rule.id,
        role_name=rule.role.name,
        element_name=rule.element.name,
        read_permission=rule.read_permission,
        read_all_permission=rule.read_all_permission,
        create_permission=rule.create_permission,
        update_permission=rule.update_permission,
        update_all_permission=rule.update_all_permission,
        delete_permission=rule.delete_permission,
        delete_all_permission=rule.delete_all_permission,
    )


@router.get("/rules", response_model=list[AccessRuleResponse])
def list_rules(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    rules = (
        db.query(AccessRoleRule)
        .options(joinedload(AccessRoleRule.role), joinedload(AccessRoleRule.element))
        .all()
    )
    return [_serialize_rule(rule) for rule in rules]


@router.post("/rules", response_model=AccessRuleResponse)
def create_rule(
    rule_data: AccessRuleSchema,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    role = db.query(Role).filter(Role.name == rule_data.role_name).first()
    element = db.query(BusinessElement).filter(BusinessElement.name == rule_data.element_name).first()
    if not role or not element:
        raise HTTPException(status_code=404, detail="Role or element not found")

    existing = (
        db.query(AccessRoleRule)
        .filter(AccessRoleRule.role_id == role.id, AccessRoleRule.element_id == element.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Rule for this role and element already exists")

    rule = AccessRoleRule(
        role_id=role.id,
        element_id=element.id,
        read_permission=rule_data.read_permission,
        read_all_permission=rule_data.read_all_permission,
        create_permission=rule_data.create_permission,
        update_permission=rule_data.update_permission,
        update_all_permission=rule_data.update_all_permission,
        delete_permission=rule_data.delete_permission,
        delete_all_permission=rule_data.delete_all_permission,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    rule.role = role
    rule.element = element
    return _serialize_rule(rule)


@router.put("/rules/{rule_id}", response_model=AccessRuleResponse)
def update_rule(
    rule_id: str,
    rule_data: AccessRuleUpdateSchema,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    rule = (
        db.query(AccessRoleRule)
        .options(joinedload(AccessRoleRule.role), joinedload(AccessRoleRule.element))
        .filter(AccessRoleRule.id == rule_id)
        .first()
    )
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    updates = rule_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return _serialize_rule(rule)
