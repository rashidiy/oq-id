import os
import sys

from fastapi import Depends, HTTPException,FastAPI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.middlewares.language import LanguageMiddleware
from utils.translations import _

from apps.models.users import User
from settings.config import AsyncSessionLocal

BASE_DIR = os.path.dirname(__file__)

sys.path.append(os.path.join(BASE_DIR, 'apps'))

app = FastAPI()
app.add_middleware(LanguageMiddleware)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class GreetingResponse(BaseModel):
    message: str


class CreateUserRequest(BaseModel):
    name: str
    email: str


@app.post("/create-user")
async def create_user(request: CreateUserRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == request.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    user = await User.create(session=session, name=request.name, email=request.email)
    return {"message": f"User {user.name} created!"}


@app.get("/greetings")
async def greetings():
    text = _("Hello, this is a message in your language!")
    return {"message": text}
