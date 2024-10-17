from managers import UserManager
from models import Base
from sqlalchemy import BigInteger, Boolean, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base, UserManager):
    first_name: Mapped[str] = mapped_column(String(25), nullable=True)
    last_name: Mapped[str] = mapped_column(String(25), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(6), nullable=True)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=True)
    bio: Mapped[str] = mapped_column(String(250), nullable=True)
    avatar: Mapped[str] = mapped_column(String(250), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger(), nullable=True, unique=True)
    developer_mode: Mapped[bool] = mapped_column(Boolean, default=False)

    # One-to-many
    permissions: Mapped[list['UserPermission']] = relationship(back_populates='user', lazy='selectin')
    companies: Mapped[list['Company']] = relationship(back_populates='user', lazy='selectin')

    @property
    def to_dict(self):
        """users data including None values, exclude sensitive fields."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "gender": self.gender,
            "birth_date": self.birth_date,
            "bio": self.bio,
            "avatar": self.avatar,
            "email": self.email,
            "telegram_id": self.telegram_id,
            "developer_mode": self.developer_mode,
        }


    def __str__(self):
        return f'{self.phone_number} {self.first_name}'
