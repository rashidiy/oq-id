import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from apis.oq_auth import router as api_auth_router
from routers.apps import router as applications_router
from routers.auth import router as auth_router
from routers.users import router as users_router
from utils.middlewares.language import LanguageMiddleware

BASE_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_DIR, 'apps'))

load_dotenv()

routers = [auth_router, users_router, applications_router, api_auth_router]
middlewares = [LanguageMiddleware]

app = FastAPI(title="OQ-ID APIGATEWAY", version="1.0", docs_url='/')
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


def init_middlewares():
    for middleware in middlewares:
        app.add_middleware(middleware)


def load_routers():
    for router in routers:
        app.include_router(router)


init_middlewares()
load_routers()
