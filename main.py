from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.models.users import User
from settings.config import AsyncSessionLocal

app = FastAPI()


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()



class CreateUserRequest(BaseModel):
    name: str
    email: str


@app.post("/create-user")
async def create_user(request: CreateUserRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == request.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    user = await User.create(session=session, name=request.name, email=request.email)
    return {"message": f"User {user.name} created!"}


@app.get("/greetings")
async def greetings():
    return {"message": "Assalomu alaykum, bu sizning tilingizdagi xabar!"}
