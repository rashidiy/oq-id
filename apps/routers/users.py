from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from settings.config import get_session
from utils.jwt import verify_token
from utils.translations import _  # noqa

router = APIRouter()
http_bearer = HTTPBearer()


@router.get("/get_me")
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
                 db: AsyncSession = Depends(get_session)):
    token = credentials.credentials
    payload = verify_token(token)

    user = await User.get_user_by_phone_number(db, payload['sub'])
    if not user:
        raise HTTPException(status_code=404, detail=_("User not found"))

    return {
        "message": _("You are authorized!"),
        "user": {
            "user_id": user.id,
            "phone_number": user.phone_number,
        }
    }
