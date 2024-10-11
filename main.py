import os
import sys

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from utils.middlewares.language import LanguageMiddleware
from utils.translations import _

from settings.config import AsyncSessionLocal

BASE_DIR = os.path.dirname(__file__)

sys.path.append(os.path.join(BASE_DIR, 'apps'))

app = FastAPI()
app.add_middleware(LanguageMiddleware)  # noqa


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class GreetingResponse(BaseModel):
    message: str


@app.get("/greetings")
async def greetings():
    text = _("Hello, this is a message in your language!")
    return {"message": text}
