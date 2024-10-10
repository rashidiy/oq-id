import os
import sys

from fastapi import FastAPI
from pydantic import BaseModel

from utils.middlewares.language import LanguageMiddleware
from utils.translations import _

BASE_DIR = os.path.dirname(__file__)

sys.path.append(os.path.join(BASE_DIR, 'apps'))

app = FastAPI()
app.add_middleware(LanguageMiddleware)


class GreetingResponse(BaseModel):
    message: str


@app.get("/greetings", response_model=GreetingResponse)
async def greetings():
    text = _("Hello, this is a message in your language!")
    return {"message": text}
