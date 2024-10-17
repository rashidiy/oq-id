from fastapi import APIRouter
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/api/v1", tags=["Auth"])

http_bearer = HTTPBearer()
