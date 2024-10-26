from fastapi import APIRouter
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/users", tags=["Users"])

http_bearer = HTTPBearer()
