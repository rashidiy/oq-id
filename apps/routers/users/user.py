from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from forms.user import UserUpdateRequest
from models.users import User
from utils.translations import trans as _

router = APIRouter(prefix="/api/v1", tags=["Users"])
http_bearer = HTTPBearer()


@router.get("/get_me")
async def get_me(user: User = Depends(User.current)):
    if not user:
        raise HTTPException(status_code=404, detail=_("User not found"))

    return {
        "success": True,
        "message": _("You are authorized!"),
        "user_forms": user.to_dict
    }


@router.patch("/update_user", response_model=dict)
async def patch_user(update_data: UserUpdateRequest, user: User = Depends(User.current)):
    for field, value in update_data:
        if value is not None:
            if field == "birth_date":
                try:
                    user.birth_date = datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    raise HTTPException(status_code=400, detail=_("Invalid date format. Use YYYY-MM-DD."))
            else:
                setattr(user, field, value)

    await User.update_user(user)
    return {"success": True, "message": _("User updated successfully"), "user_forms": user.to_dict}
