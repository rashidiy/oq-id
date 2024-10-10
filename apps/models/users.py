from datetime import datetime

from sqlalchemy import String, DateTime, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(AsyncAttrs, DeclarativeBase):
    @declared_attr
    def __tablename__(self) -> str:
        __name = self.__name__.lower()
        if __name.endswith('y'):
            __name = __name[:-1] + 'ie'
        return __name + 's'


class BaseModel(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        instance = cls(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance


class User(BaseModel):
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
