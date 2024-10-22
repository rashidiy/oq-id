from models import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserPermission(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    app_id: Mapped[int] = mapped_column(ForeignKey('apps.id', ondelete='CASCADE'), nullable=False)

    # Many-to-one
    user: Mapped['User'] = relationship(back_populates='permissions')
    app: Mapped['App'] = relationship(back_populates='permissions')
