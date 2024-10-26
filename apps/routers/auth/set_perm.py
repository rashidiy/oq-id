from fastapi import HTTPException, Depends
from pydantic import BaseModel

from models import UserPermission, App, User
from utils.translations import trans as _
from .base import router


class GrantPermissionRequest(BaseModel):
    app_id: int


@router.post("/set_permission", status_code=201)
async def create_permission(
        permission_data: GrantPermissionRequest,
        current_user=Depends(User.current)):
    """
    Create a new permission for the authenticated user and a specified app.

    Parameters:
    permission_data : containing the app_id.
    current_user (User, optional): The authenticated user.

    Returns:
    dict: A dictionary containing the success status, message, and the created permission.
    """

    app = await App.get_obj_or_404(id=permission_data.app_id)

    if await current_user.item_exists(user_id=current_user.id, app_id=app.id):
        raise HTTPException(status_code=400, detail=_("Permission already exists for this user and app."))

    await UserPermission.create(user_id=current_user.id, app_id=app.id)

    return {
        "success": True,
        "message": _("Permission assigned successfully!"),
        "permission": {
            "user_id": current_user.id,
            "app_id": app.id,
        }
    }
