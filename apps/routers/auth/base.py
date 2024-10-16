from fastapi import APIRouter
from fastapi.security import HTTPBearer

router = APIRouter()

http_bearer = HTTPBearer()
