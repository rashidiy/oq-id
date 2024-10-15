import os
import sys

from fastapi import FastAPI

from routers.users import router as user_router
from routers.auth import router as auth_router
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
app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
