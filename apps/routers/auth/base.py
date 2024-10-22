from fastapi import APIRouter
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/auth", tags=["Auth"])

http_bearer = HTTPBearer()
