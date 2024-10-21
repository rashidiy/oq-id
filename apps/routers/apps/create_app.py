from fastapi import UploadFile, File
from fastapi.params import Form, Depends
from starlette.responses import JSONResponse

from managers import PassManager
from models import User, App, AppType
from .base import router
from utils.translations import trans as _
from utils.validators import validated_redirect_url


@router.post('/create')
async def create_app(
        user: User = Depends(User.developer),
        name: str = Form(...),
        app_type: AppType = Form(...),
        redirect_url: str = Depends(validated_redirect_url),
        logo: UploadFile = File(...)
):
    """
        Create a new app.

        This endpoint lets you create a new app and generate a unique token for it.

        - **name**: The name of the app (required).
        - **app_type**: The type of the app (e.g., web, mobile) (required).
        - **redirect_url**: The URL where users are redirected after authentication (required).
        - **logo**: A logo image for the app (will be resized to 250x250).

        Returns:
        - Success message and the app's details, including a token for future API use.
    """

    secret_key = App.generate_secret_key()
    app = await App.create(
        user_id=user.id,
        name=name,
        type=app_type,
        redirect_url=redirect_url,
        secret_hash=PassManager.hash_password(secret_key)
    )
    await App.process_image(
        file=logo, width=250, height=250, upload_file_path=f'./uploads/apps/logos/{app.id}.png'
    )
    return JSONResponse(content={
        'success': True,
        'message': _('App has been created successfully'),
        'result': app.to_dict('id', 'name', 'type', 'logo', 'redirect_url') | {"token": f'{app.id}:{secret_key}'}
    })
