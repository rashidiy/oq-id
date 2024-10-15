import os
import sys

from fastapi import FastAPI

from routers.auth.login import router as login_router
from routers.auth.register import router as register_router
from routers.auth.reset_password import router as reset_password
from routers.users import router as user_router
from utils.middlewares.middlewares import init_middlewares

BASE_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_DIR, 'apps'))

app = FastAPI(
    title="OQ-ID APIGATEWAY",
    version="1.0",
    docs_url='/',
)

init_middlewares(app)
app.include_router(user_router, prefix="/api/v1", tags=["Users"])
app.include_router(register_router, prefix="/api/v1", tags=["Auth"])
app.include_router(login_router, prefix="/api/v1", tags=["Auth"])

app.include_router(reset_password, prefix="/api/v1", tags=["Auth"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
