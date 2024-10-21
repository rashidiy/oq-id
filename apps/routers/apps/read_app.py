from fastapi.params import Depends

from models import User, App
from .base import router


@router.get('/all')
async def get_all_apps(user: User = Depends(User.developer)):
    """
        Get all your apps.

        This endpoint returns a list of all apps created by you.

        - Returns:
            - A list of your apps, including each app's ID, name, type, logo URL, and redirect URL.
    """
    apps = [
        app.to_dict('id', 'name', 'type', 'logo', 'redirect_url')
        for app in user.apps
    ]
    return {'status': True, 'result': apps}


@router.get('/detail')
async def detail_app(app_id: int, user: User = Depends(User.developer)):
    """
        Get app details.

        Use this endpoint to view details of a specific app by its ID.

        - **app_id**: The ID of the app you want to view (required).

        Returns:
        - Detailed information about the app, including ID, name, type, logo URL, and redirect URL.
    """
    app = await App.get_obj_or_404(id=app_id, user_id=user.id)
    return {
        'success': True,
        'result': app.to_dict('id', 'name', 'type', 'logo', 'redirect_url')
    }
