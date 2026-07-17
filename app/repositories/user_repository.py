from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from ..models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[User]:
        """Получить всех пользовтелей"""
        result = await self.db.execute(select(User).where(User.deleted_at.is_(None)))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Optional[User]:
        """Получить пользователя по id"""
        result = await self.db.execute(
            select(User).where(User.id == id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[User]:
        """Получить пользователя по имени"""
        result = await self.db.execute(
            select(User).where(User.name == name, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> User:
        """передается data: dict а не pydantic модель для того чтобы захешировать пароль"""
        new_user = User(**data)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def delete(self, id: int) -> bool:
        """Удалить пользователя (soft delete)"""
        user = await self.get_by_id(id)
        if not user:
            return False
        user.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()
        return True

    async def update(self, id: int, update_data: dict) -> Optional[User]:
        """Обновить данные пользователя"""
        user = await self.get_by_id(id)
        if not user:
            return None

        for key, value in update_data.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user