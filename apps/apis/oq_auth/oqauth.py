from fastapi import HTTPException
from starlette import status

from .base import router
from apis.oq_auth.exchange_codes import validate_user_permission
from apis.oq_auth.schemas import PermissionSchema
from managers import PassManager
from models import App
from utils.translations import trans as _


@router.post('/user')
async def get_token(schema: PermissionSchema):
    app_id, token_body = schema.token.split(':')
    app = await App.get(id=int(app_id))

    is_token_valid = PassManager.verify_password(token_body, app.secret_hash)
    if not is_token_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_('Invalid token')
        )

    await validate_user_permission(app_id, schema.user_id)

    return {
        'success': True,
        'result': {
            'user_id': schema.user_id,
            'redirect': app.redirect_url
        }
    }
