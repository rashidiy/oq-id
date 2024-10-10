import os
import sys

from fastapi import FastAPI
from pydantic import BaseModel

from utils.middlewares.language import LanguageMiddleware

sys.path.append(os.path.join(os.path.dirname(__file__), 'apps'))

app = FastAPI()
app.add_middleware(LanguageMiddleware)


class GreetingResponse(BaseModel):
    message: str


@app.get("/greetings", response_model=GreetingResponse)
async def greetings():
    return {"message": "Hello, this is a message in your language!"}
