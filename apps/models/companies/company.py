from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base


class Company(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    logo: Mapped[str] = mapped_column(String(250))
    redirect_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    secret_key: Mapped[str] = mapped_column(String(16), nullable=False)

    user: Mapped['User'] = relationship(back_populates="companies")
    permissions: Mapped[list['UserPermission']] = relationship(back_populates="company")
