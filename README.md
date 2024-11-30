# OQ-ID

Identity and authentication service for the OQ ecosystem. Handles user registration, login, JWT-based auth, role management, and third-party app registration — all via an async FastAPI backend.

## Stack

- **Framework**: FastAPI 0.115 (with all extras)
- **DB**: PostgreSQL + SQLAlchemy 2.0 (async, asyncpg)
- **Migrations**: Alembic
- **Auth**: JWT (python-jose), bcrypt, passlib
- **Cache**: Redis (aioredis, async)
- **Rate limiting**: slowapi
- **i18n**: Uzbek, Russian, English (gettext)
- **Server**: Uvicorn
- **Package manager**: Poetry

## Features

- User registration and login with JWT access/refresh tokens
- Role-based access control
- App (client) management — register third-party apps in the ecosystem
- User avatar uploads (Pillow)
- Rate limiting on sensitive endpoints
- Trilingual API responses (uz/ru/en)
- Modular router structure with separate namespaces for auth, users, and apps

## Project Structure

```
apps/
  apis/oq_auth/     — auth endpoints
  routers/
    auth/           — login, refresh, logout
    users/          — user CRUD
    apps/           — app registration
  models/
    users/
    apps/
  managers/
    user_manager.py
    pass_manager.py
    app_manager.py
  utils/
    translations.py
    services/
    validators/
  forms/            — Pydantic schemas
  db/database.py    — async session setup
alembic/versions/   — DB migrations
translations/       — uz/ru/en .po/.mo files
```

## Getting Started

```bash
poetry install
cp .env.example .env

alembic upgrade head
uvicorn main:app --reload
```

## Makefile

```bash
make run        # start the server
make migrate    # apply alembic migrations
make revision   # generate new migration
```
