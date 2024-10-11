from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import (DeclarativeBase, Mapped, declared_attr,
                            mapped_column, relationship)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str: 
        name = cls.__name__.lower()
        if name.endswith('y'):
            name = name[:-1] + 'ie'
        return name + 's'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        instance = cls(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance


class User(Base):
    first_name: Mapped[str] = mapped_column(String(25), nullable=False)
    last_name: Mapped[str] = mapped_column(String(25), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(6))
    birth_date: Mapped[Date] = mapped_column(Date)
    bio: Mapped[str] = mapped_column(String(250))
    avatar: Mapped[str] = mapped_column(String(250))
    email: Mapped[str] = mapped_column(String(25), unique=True)
    telegram_id: Mapped[str] = mapped_column(BigInteger(), unique=True)
    developer_mode: Mapped[bool] = mapped_column(Boolean, default=False)

    # One-to-many
    permissions: Mapped[list['UserPermission']] = relationship(back_populates='user', lazy='selectin')
    companies: Mapped[list['Company']] = relationship(back_populates='user', lazy='selectin')


class UserPermission(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)

    # Many-to-one
    user: Mapped['User'] = relationship(back_populates='permissions')
    company: Mapped['Company'] = relationship(back_populates='permissions')


class Company(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    logo: Mapped[str] = mapped_column(String(250))
    redirect_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    secret_key: Mapped[str] = mapped_column(String(16), nullable=False)

    # Many-to-one relationship with User and one-to-many relationship with UserPermission
    user: Mapped['User'] = relationship(back_populates="companies")
    permissions: Mapped[list['UserPermission']] = relationship(back_populates="company")
