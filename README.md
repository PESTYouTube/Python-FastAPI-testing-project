# Система аутентификации и авторизации (FastAPI)

Backend с **собственной** реализацией входа и разграничения доступа: пароли хешируются через **bcrypt**, сессия пользователя — **JWT** (Cookie и заголовок `Authorization: Bearer`).

## Схема управления доступом

### Сущности

| Таблица | Назначение |
|---------|------------|
| `users` | Учётные записи (email, ФИО, пароль, `is_active`) |
| `roles` | Роли: `admin`, `manager`, `user`, `guest` |
| `user_roles` | Связь пользователь ↔ роль (M2M) |
| `business_elements` | Ресурсы приложения: `products`, `shops`, `orders`, `users`, `access_rules` |
| `access_roles_rules` | Правила: какая роль что может делать с элементом |

### Права в `access_roles_rules`

| Поле | Смысл |
|------|--------|
| `read_permission` | Читать **свои** объекты (`owner_id = user.id`) |
| `read_all_permission` | Читать **все** объекты |
| `create_permission` | Создавать |
| `update_permission` | Изменять **свои** |
| `update_all_permission` | Изменять **все** |
| `delete_permission` | Удалять **свои** |
| `delete_all_permission` | Удалять **все** |

Роль `admin` в коде имеет полный доступ без проверки правил.

### Поток запроса

1. **Аутентификация** — `AuthMiddleware` и `get_current_user` извлекают JWT из Cookie или `Authorization: Bearer`, кладут пользователя в `request.state.user`.
2. **Авторизация** — для mock-ресурсов проверяются правила по ролям пользователя.
3. **401** — токен отсутствует, невалиден или пользователь деактивирован (`is_active=False`).
4. **403** — пользователь известен, но нет права на ресурс.

## Запуск

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Документация API: http://127.0.0.1:8000/docs

PostgreSQL (опционально):

```bash
set DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/authdb
```

При смене схемы БД удалите файл `app.db` (SQLite), чтобы таблицы пересоздались.

## Тестовые пользователи (создаются при старте)

| Email | Пароль | Роль |
|-------|--------|------|
| admin@example.com | admin123 | admin |
| manager@example.com | manager123 | manager |
| user@example.com | user1234 | user |

## API

### Пользователь

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация (имя, фамилия, отчество, email, пароль ×2) |
| POST | `/auth/login` | Вход, JWT в Cookie и в теле ответа |
| POST | `/auth/logout` | Выход |
| GET | `/users/me` | Профиль |
| PUT | `/users/me` | Обновление профиля |
| DELETE | `/users/me` | Мягкое удаление (`is_active=False`) + logout |

### Администратор (роль `admin`)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/admin/permissions/rules` | Список правил |
| POST | `/admin/permissions/rules` | Создать правило |
| PUT | `/admin/permissions/rules/{rule_id}` | Изменить правило |

### Mock-бизнес-ресурсы

| Метод | Путь | Элемент |
|-------|------|---------|
| GET | `/api/products` | products |
| GET | `/api/products/{id}` | products |
| GET | `/api/shops` | shops |
| GET | `/api/orders` | orders |
| POST | `/api/orders` | orders (create) |

## Пример

```bash
# Вход
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user@example.com\",\"password\":\"user1234\"}"

# Список товаров (только свои, если нет read_all)
curl http://127.0.0.1:8000/api/products \
  -H "Authorization: Bearer <token>"
```
