from enum import Enum as PyEnum

from sqlalchemy import ForeignKey, String, BigInteger, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from managers import AppManager
from models import Base


class AppType(PyEnum):
    WEB = "web"
    MOBILE = "mobile"

    def __str__(self):
        return self.value


class App(Base, AppManager):
    id: Mapped[str] = mapped_column(BigInteger, primary_key=True, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    type: Mapped[AppType] = mapped_column(Enum(AppType), nullable=False)
    logo: Mapped[str] = mapped_column(String(250), nullable=True)
    redirect_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    secret_hash: Mapped[str] = mapped_column(String(250), nullable=False)

    user: Mapped['User'] = relationship(back_populates="apps")
    permissions: Mapped[list['UserPermission']] = relationship(back_populates="app")
