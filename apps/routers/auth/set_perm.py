from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select

from db import BaseManager
from models import UserPermission, User, App
from utils.translations import trans as _
from .base import router


class GrantPermissionRequest(BaseModel):
    app_id: int


@router.post("/set_permission", status_code=201)
async def create_permission(
        permission_data: GrantPermissionRequest,
        current_user: User = Depends(User.current)
):
    """Create a new permission for the authenticated user and a specified app."""

    async with BaseManager._get_session() as session:
        app = await App.get_obj_or_404(id=permission_data.app_id)

        existing_permission = await session.execute(
            select(UserPermission).where(
                UserPermission.user_id == current_user.id,
                UserPermission.app_id == app.id
            )
        )
        if existing_permission.scalars().first() is not None:
            raise HTTPException(status_code=400, detail=_("Permission already exists for this user and app."))

        new_permission = UserPermission(user_id=current_user.id, app_id=app.id)
        session.add(new_permission)
        await session.commit()

    return {
        "success": True,
        "message": _("Permission created successfully"),
        "permission": {
            "user_id": current_user.id,
            "app_id": new_permission.app_id,
        }
    }
