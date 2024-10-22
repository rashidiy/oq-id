from fastapi.params import Depends

from models import User, App
from .base import router


@router.get('/all')
async def get_all_apps(user: User = Depends(User.developer)):
    apps = [
        app.to_dict('id', 'name', 'type', 'logo', 'redirect_url')
        for app in user.apps
    ]
    return {'status': True, 'result': apps}


@router.get('/detail')
async def detail_app(app_id: int, user: User = Depends(User.developer)):
    app = await App.get_obj_or_404(id=app_id, user_id=user.id)
    return {
        'success': True,
        'result': app.to_dict('id', 'name', 'type', 'logo', 'redirect_url')
    }
