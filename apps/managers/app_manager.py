import secrets
import string

from db import BaseManager


class AppManager(BaseManager):
    @staticmethod
    def generate_secret_key(length: int = 48) -> str:
        chars = string.ascii_letters + string.digits
        return ''.join('-' if _ in [8, 18, 30] else secrets.choice(chars) for _ in range(length))

    @classmethod
    async def create(cls, **kwargs):
        """Creates a new object and stores it in the DB."""
        if not (app_id := kwargs.get('app_id')):
            app_id = await cls.unordered_id()
            kwargs['id'] = app_id
        if 'logo' not in kwargs:
            kwargs['logo'] = f'/uploads/apps/logos/{app_id}.png'
        return await super().create(**kwargs)
