from sqlalchemy.orm import Session

from crud import get_password_hash
from models.models import AccessRoleRule, BusinessElement, Role, User

# Фиксированные id для демо-пользователей и mock-объектов
ADMIN_USER_ID = "10000000-0000-0000-0000-000000000001"
MANAGER_USER_ID = "10000000-0000-0000-0000-000000000002"
REGULAR_USER_ID = "10000000-0000-0000-0000-000000000003"

ROLES = [
    ("admin", "Администратор системы"),
    ("manager", "Менеджер"),
    ("user", "Обычный пользователь"),
    ("guest", "Гость"),
]

ELEMENTS = [
    ("products", "Товары"),
    ("shops", "Магазины"),
    ("orders", "Заказы"),
    ("users", "Пользователи"),
    ("access_rules", "Правила доступа"),
]

RULES = {
    "admin": {name: (True,) * 7 for name, _ in ELEMENTS},
    "manager": {
        "products": (True, True, True, True, False, False, False),
        "shops": (True, True, False, False, False, False, False),
        "orders": (True, True, True, True, False, True, False),
        "users": (True, False, False, False, False, False, False),
        "access_rules": (False,) * 7,
    },
    "user": {
        "products": (True, False, False, True, False, False, False),
        "shops": (True, False, False, False, False, False, False),
        "orders": (True, False, True, True, False, False, False),
        "users": (False,) * 7,
        "access_rules": (False,) * 7,
    },
    "guest": {
        "products": (True, False, False, False, False, False, False),
        "shops": (False,) * 7,
        "orders": (False,) * 7,
        "users": (False,) * 7,
        "access_rules": (False,) * 7,
    },
}

DEMO_USERS = [
    {
        "id": ADMIN_USER_ID,
        "email": "admin@example.com",
        "password": "admin123",
        "name": "Админ",
        "surname": "Системный",
        "patronymic": "Тестович",
        "role": "admin",
    },
    {
        "id": MANAGER_USER_ID,
        "email": "manager@example.com",
        "password": "manager123",
        "name": "Мария",
        "surname": "Менеджерова",
        "patronymic": None,
        "role": "manager",
    },
    {
        "id": REGULAR_USER_ID,
        "email": "user@example.com",
        "password": "user1234",
        "name": "Иван",
        "surname": "Пользователев",
        "patronymic": "Иванович",
        "role": "user",
    },
]


def _rule_tuple_to_model(role_id: str, element_id: str, perms: tuple[bool, ...]) -> AccessRoleRule:
    return AccessRoleRule(
        role_id=role_id,
        element_id=element_id,
        read_permission=perms[0],
        read_all_permission=perms[1],
        create_permission=perms[2],
        update_permission=perms[3],
        update_all_permission=perms[4],
        delete_permission=perms[5],
        delete_all_permission=perms[6],
    )


def seed_database(db: Session) -> None:
    if db.query(Role).first():
        return

    roles: dict[str, Role] = {}
    for name, description in ROLES:
        role = Role(name=name, description=description)
        db.add(role)
        roles[name] = role
    db.flush()

    elements: dict[str, BusinessElement] = {}
    for name, description in ELEMENTS:
        element = BusinessElement(name=name, description=description)
        db.add(element)
        elements[name] = element
    db.flush()

    for role_name, element_rules in RULES.items():
        for element_name, perms in element_rules.items():
            db.add(
                _rule_tuple_to_model(
                    roles[role_name].id,
                    elements[element_name].id,
                    perms,
                )
            )

    for data in DEMO_USERS:
        user = User(
            id=data["id"],
            email=data["email"],
            name=data["name"],
            surname=data["surname"],
            patronymic=data["patronymic"],
            hashed_password=get_password_hash(data["password"]),
            is_active=True,
        )
        user.roles.append(roles[data["role"]])
        db.add(user)

    db.commit()
