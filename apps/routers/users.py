from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from apps.models.auth.user import User
from settings.config import get_session

router = APIRouter()


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    password_hash: str
    gender: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    telegram_id: Optional[int] = None
    developer_mode: Optional[bool] = False


class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone_number: str
    email: Optional[str]
    developer_mode: bool


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    user_data = user.dict()

    if user_data.get("birth_date"):
        user_data["birth_date"] = datetime.strptime(user_data["birth_date"], "%Y-%m-%d").date()

    new_user = User(**user_data)
    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/users/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(get_session)):
    query = await db.execute(select(User).filter_by(id=user_id))
    user = query.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(user_id: int, updated_user: UserCreate, db: AsyncSession = Depends(get_session)):
    query = await db.execute(select(User).filter_by(id=user_id))
    user = query.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in updated_user.dict(exclude_unset=True).items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_session)):
    query = await db.execute(select(User).filter_by(id=user_id))
    user = query.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}
