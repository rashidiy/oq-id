from fastapi.params import Depends

from forms.apps import AppRequest
from models import User, App
from .base import router
from utils.translations import trans as _


@router.delete('/delete')
async def delete_app(
        data: AppRequest,
        user: User = Depends(User.developer)
):
    """
        Delete an app.

        This endpoint deletes one of your apps.

        - **json-body**: The app's ID (`app_id`) you want to delete (required).

        Returns:
        - Success message confirming the app was deleted.
    """
    app = await App.get_obj_or_404(id=data.app_id, user_id=user.id)
    await App.delete(app)
    return {
        'success': True,
        'message': _('App has been deleted successfully'),
    }
