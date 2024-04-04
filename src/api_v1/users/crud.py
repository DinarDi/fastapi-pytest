from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result

from .schemas import UserCreate
from database import User


async def create_user(
        session: AsyncSession,
        payload: UserCreate,
) -> User:
    """Создание пользователя"""
    user = User(**payload.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_users(session: AsyncSession) -> list[User]:
    """Получение всех пользователей"""
    stmt = select(User)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)
