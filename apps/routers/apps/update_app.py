from typing import Optional

from fastapi import UploadFile, File, HTTPException
from fastapi.params import Form, Depends
from starlette.responses import JSONResponse

from forms.apps import AppRequest, TokenRegenerateConfirm
from managers import PassManager
from models import User, App, AppType
from .base import router
from utils.services import AuthService, OTPManager
from utils.translations import trans as _
from utils.validators import validate_redirect_url_on_update


@router.post('/pre_regenerate_token')
async def request_to_regenerate_token(
        data: AppRequest,
        user: User = Depends(User.developer),
):
    app = await App.get_obj_or_404(id=data.app_id, user_id=user.id)
    await AuthService.send_verification_code(user.phone_number, f'create_app:{app.id}')
    return {
        "success": True,
        "message": _("Verification code sent to {phone_number}").format(phone_number=user.phone_number)
    }


@router.post('/regenerate_token')
async def confirm_regeneration_of_token(
        data: TokenRegenerateConfirm,
        user: User = Depends(User.developer)
):
    app = await App.get_obj_or_404(id=data.app_id, user_id=user.id)
    otp = await OTPManager.get_otp(user.phone_number, f"create_app:{app.id}")
    if not otp or otp != data.verification_code:
        raise HTTPException(status_code=400, detail=_("Invalid OTP or OTP expired."))
    secret_key = App.generate_secret_key()
    app.secret_hash = PassManager.hash_password(secret_key)
    await App.update(app)
    return {
        'success': True,
        'message': _('App token has been regenerated successfully'),
        'result': {
            'app_id': app.id,
            'token': f'{app.id}:{secret_key}',
        }
    }


@router.patch('/update')
async def update_app(
        user: User = Depends(User.developer),
        app_id: int = Form(...),
        name: Optional[str] = Form(None),
        app_type: Optional[AppType] = Form(None),
        redirect_url: Optional[str] = Depends(validate_redirect_url_on_update),
        logo: Optional[UploadFile] = File(None)
):
    app = await App.get_obj_or_404(id=app_id, user_id=user.id)
    touched = False
    if name:
        touched = True
        app.name = name
    if app_type:
        touched = True
        app.type = app_type
    if redirect_url:
        touched = True
        app.redirect_url = redirect_url
    if logo:
        await App.process_image(
            file=logo, width=250, height=250, upload_file_path=f'./uploads/apps/logos/{app.id}.png'
        )
    if touched:
        await App.update(app)
    return JSONResponse(content={
        'success': True,
        'message': _('App has been created successfully'),
        'result': app.to_dict('id', 'name', 'type', 'logo', 'redirect_url')
    })
