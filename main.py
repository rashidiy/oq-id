import os
import sys

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from settings.config import AsyncSessionLocal
from utils.middlewares.language import LanguageMiddleware
from utils.translations import _

BASE_DIR = os.path.dirname(__file__)

sys.path.append(os.path.join(BASE_DIR, 'apps'))
app = FastAPI(
    title="OQ-ID APIGATEWAY",
    version="1.0",
    docs_url='/',
)
app.add_middleware(LanguageMiddleware)  # noqa


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class GreetingResponse(BaseModel):
    message: str


@app.get("/greetings", name="Greet in Language", tags=["Greeting"])
async def greetings():
    text = _("Hello, this is a message in your language!")
    return {"message": text}
