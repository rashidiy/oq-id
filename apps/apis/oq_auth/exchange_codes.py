import json
import secrets
import string

from fastapi import HTTPException, Depends
from starlette import status

from .base import router
from apis.oq_auth.schemas import GenerateAuthCodeReq, ExchangeAuthCodeReq
from models import User, UserPermission
from settings.config import redis_client
from utils.services import TokenManager
from utils.translations import trans as _


async def validate_user_permission(app_id: str, user_id: int):
    """
    Validates if the user has permission for the given app.
    """
    permission = await UserPermission.get_obj_or_404(app_id=int(app_id), user_id=user_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_('Permission denied')
        )


@router.post("/generate_authorisation_code", status_code=status.HTTP_200_OK)
async def generate_authorisation_code(data: GenerateAuthCodeReq, user: User = Depends(User.current)):
    """
    Generates an authorization code for a user and app after validating permissions.
    """
    await validate_user_permission(data.app_id, user.id)

    auth_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))

    redis_payload = {
        "phone_number": user.phone_number,
        "app_id": data.app_id,
        "scope": data.scope
    }
    redis_key = f"auth_code:{user.phone_number}:{auth_code}"

    await redis_client.setex(redis_key, 300, json.dumps(redis_payload))
    return {"success": True, "code": auth_code}


@router.post("/exchange_code", status_code=status.HTTP_200_OK)
async def exchange_code(data: ExchangeAuthCodeReq, user: User = Depends(User.current)):
    """
    Exchanges an authorization code for an access token after validating the code and user.
    """
    auth_code_key = f"auth_code:{user.phone_number}:{data.code}"
    auth_code_data = await redis_client.get(auth_code_key)

    if not auth_code_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_("Invalid or expired authorization code")
        )

    auth_code_data = json.loads(auth_code_data)

    if auth_code_data.get("phone_number") != user.phone_number:
        print(auth_code_data)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_("This code does not belong to the current user!")
        )

    access_token = TokenManager.create_access_token(
        data={
            "sub": auth_code_data["phone_number"],
            "app_id": auth_code_data["app_id"],
            "scope": auth_code_data["scope"],
        }
    )
    await redis_client.delete(auth_code_key)
    return {"success": True, "access_token": access_token}
