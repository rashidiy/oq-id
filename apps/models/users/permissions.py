from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base


class UserPermission(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)

    # Many-to-one
    user: Mapped['User'] = relationship(back_populates='permissions')
    company: Mapped['Company'] = relationship(back_populates='permissions')
