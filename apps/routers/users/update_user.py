from datetime import datetime

from fastapi import Depends, HTTPException, Request

from forms.user import UserUpdateRequest
from models.users import User
from settings.config import limiter
from utils.translations import trans as _
from .base import router

@router.get("/get_me")
@limiter.limit("2/240 seconds", error_message="Too many requests, please try again in 90 seconds.")
async def get_me(request: Request, user: User = Depends(User.current)):
    if not user:
        raise HTTPException(status_code=404, detail=_("User not found"))
    return {"success": True, "data": user.to_dict}


@router.patch("/update_user", response_model=dict)
async def patch_user(update_data: UserUpdateRequest, user: User = Depends(User.current)):
    """
    Updates the user's information based on the provided data.

    Parameters:
    - update_data (json): An object containing the fields and their new values to be updated.
    - user (User, optional): The current user object. If not provided, it will be fetched from the request context.

    Returns:
    dict: A dictionary containing the success status, a message indicating the update status, and the updated user's data.
    """
    for field, value in update_data:
        if value is not None:
            if field == "birth_date":
                try:
                    user.birth_date = datetime.strptime(value, '%d.%m.%Y').date()
                except ValueError:
                    raise HTTPException(status_code=400, detail=_("Invalid date format. Use DD.MM.YYYY."))
            else:
                setattr(user, field, value)

    await User.update(user)
    return {"success": True, "message": _("User updated successfully"), "data": user.to_dict}
