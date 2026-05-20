from db.seed import ADMIN_USER_ID, MANAGER_USER_ID, REGULAR_USER_ID

MOCK_PRODUCTS = [
    {"id": "p1", "name": "Ноутбук", "price": 89990, "owner_id": ADMIN_USER_ID},
    {"id": "p2", "name": "Мышь", "price": 1990, "owner_id": REGULAR_USER_ID},
    {"id": "p3", "name": "Клавиатура", "price": 4990, "owner_id": MANAGER_USER_ID},
]

MOCK_SHOPS = [
    {"id": "s1", "name": "Центральный", "city": "Москва", "owner_id": ADMIN_USER_ID},
    {"id": "s2", "name": "Северный", "city": "СПб", "owner_id": MANAGER_USER_ID},
]

MOCK_ORDERS = [
    {"id": "o1", "product": "Ноутбук", "status": "new", "owner_id": REGULAR_USER_ID},
    {"id": "o2", "product": "Мышь", "status": "done", "owner_id": REGULAR_USER_ID},
    {"id": "o3", "product": "Клавиатура", "status": "processing", "owner_id": MANAGER_USER_ID},
]
