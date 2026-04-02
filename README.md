# oq-id

Centralized identity service for the OQ platform — phone-based authentication with OTP verification, JWT access/refresh tokens, and OAuth-like application registration.

Think of it as a lightweight Auth0 for the OQ ecosystem: other services delegate authentication here rather than implementing their own.

---

## Auth flow

```
1. POST /pre_register  →  send OTP to phone number (Redis, 1 OTP per 90s rate limit)
2. POST /register      →  verify OTP → create User → return JWT access + refresh pair

3. POST /pre_login     →  validate credentials → send OTP to phone
4. POST /login         →  verify OTP → return JWT access + refresh pair

5. POST /refresh_token →  exchange refresh token → new access token

Password reset:
6. POST /pre_reset_password  →  send OTP to phone
7. POST /reset_password      →  verify OTP → update password hash

Contact change:
8. PATCH /change_contact         →  send OTP to new phone/email
9. PATCH /verify_contact_change  →  verify OTP → update contact → re-issue tokens
```

OTPs are stored in Redis with an expiry. `slowapi` enforces a rate limit (one OTP per 90 seconds per phone number) to prevent spam.

---

## Application registration

The service doubles as an OAuth-like app registry. Developers register their apps and get a `secret_hash` for server-to-server calls:

```
POST /apps/create  →  register App (name, type: WEB/MOBILE, logo, redirect_url)
GET  /apps/{id}    →  read app details
PATCH /apps/{id}   →  update app
DELETE /apps/{id}  →  remove app
```

`developer_mode` must be enabled on the user account before app creation is allowed.

`UserPermission` links users to apps — tracking which users have authorized which applications.

---

## Data model

```
User
    ├── phone_number (unique)
    ├── password_hash (bcrypt)
    ├── first_name, last_name, gender, birth_date, bio
    ├── avatar (auto-resized to 250×250 px on upload)
    ├── telegram_id, email
    ├── developer_mode  ← gates app creation
    └── permissions → UserPermission → App

App
    ├── name, type (WEB / MOBILE)
    ├── logo, redirect_url
    ├── secret_hash
    └── user (owner)
```

---

## Notable details

- **OTP via Redis**: codes expire automatically, no cron job needed. `slowapi` prevents brute-force via rate limiting.
- **Async throughout**: SQLAlchemy with `asyncpg`, all endpoints are `async def`. No sync blocking in the request path.
- **Password hashing**: bcrypt via `passlib`. Passwords are never stored in plain text.
- **Image processing**: uploaded avatars are resized to 250×250 pixels using Pillow before storage.
- **Trilingual responses**: Uzbek, Russian, English — response language negotiated per request (`pybabel`).
- **JWT**: `python-jose`, separate access and refresh tokens.

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/pre_register` | Send OTP to phone |
| `POST` | `/register` | Verify OTP, create user, return JWT |
| `POST` | `/pre_login` | Validate credentials, send OTP |
| `POST` | `/login` | Verify OTP, return JWT |
| `POST` | `/refresh_token` | Refresh access token |
| `POST` | `/pre_reset_password` | Send reset OTP |
| `POST` | `/reset_password` | Update password |
| `PATCH` | `/change_contact` | Send OTP to new contact |
| `PATCH` | `/verify_contact_change` | Confirm contact change |
| `POST` | `/apps/create` | Register new app |
| `GET` | `/apps/{id}` | Get app details |
| `PATCH` | `/apps/{id}` | Update app |
| `DELETE` | `/apps/{id}` | Delete app |

---

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| DB | PostgreSQL, asyncpg |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Auth | bcrypt, python-jose (JWT) |
| Rate limiting | slowapi (Redis-backed) |
| Cache | Redis (OTP storage) |
| Images | Pillow (avatar resize) |
| i18n | pybabel |
| Package manager | Poetry |
| Python | 3.12+ |

---

## Getting started

```bash
poetry install

cp .env.example .env
# fill in DATABASE_URL, REDIS_URL, SECRET_KEY

alembic upgrade head

uvicorn main:app --reload
```

Interactive docs at `http://127.0.0.1:8000/docs`.
