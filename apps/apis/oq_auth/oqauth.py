from fastapi import APIRouter, HTTPException
from starlette import status

from apis.oq_auth.schemas import PermissionSchema
from managers import PassManager
from models import App, UserPermission
from utils.translations import trans as _

router = APIRouter(prefix="/api/v1/oq_id/access", tags=["oqauth"])


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

    p = await UserPermission.get(app_id=app_id, user_id=schema.user_id)
    if not p:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_('You do not have permission to access this resource')
        )

    return {
        'success': True,
        'result': {
            'user_id': schema.user_id,
            'redirect': app.redirect_url
        }
    }
