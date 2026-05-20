from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from core.permissions import PermissionAction, can_list_resources, user_has_permission
from db.session import get_db
from mock_data import MOCK_ORDERS, MOCK_PRODUCTS, MOCK_SHOPS
from models.models import User

router = APIRouter(prefix="/api", tags=["business-mock"])


def _filter_by_access(items: list[dict], user: User, see_all: bool) -> list[dict]:
    if see_all:
        return items
    return [item for item in items if str(item["owner_id"]) == str(user.id)]


def _require_list_access(db: Session, user: User, element: str) -> tuple[bool, bool]:
    allowed, see_all = can_list_resources(db, user, element)
    if not allowed:
        raise HTTPException(
            status_code=403,
            detail=f"Forbidden: read access to '{element}'",
        )
    return allowed, see_all


@router.get("/products")
def list_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, see_all = _require_list_access(db, current_user, "products")
    return {"items": _filter_by_access(MOCK_PRODUCTS, current_user, see_all)}


@router.get("/products/{product_id}")
def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not user_has_permission(
        db, current_user, "products", PermissionAction.READ, product["owner_id"]
    ):
        raise HTTPException(status_code=403, detail="Forbidden: read access to this product")

    return product


@router.get("/shops")
def list_shops(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, see_all = _require_list_access(db, current_user, "shops")
    return {"items": _filter_by_access(MOCK_SHOPS, current_user, see_all)}


@router.get("/orders")
def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, see_all = _require_list_access(db, current_user, "orders")
    return {"items": _filter_by_access(MOCK_ORDERS, current_user, see_all)}


@router.post("/orders")
def create_order(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user_has_permission(db, current_user, "orders", PermissionAction.CREATE):
        raise HTTPException(status_code=403, detail="Forbidden: create access to orders")

    return {
        "message": "Order created (mock)",
        "owner_id": current_user.id,
    }
