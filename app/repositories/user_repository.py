from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from ..models.user import User
from app.schemas.user import UserUpdate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.name == name))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> User:
        """передается data: dict а не pydantic модель для того чтобы захешировать пароль"""
        new_user = User(**data)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def delete(self, id: int) -> bool:
        user = await self.get_by_id(id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        else:
            return False

    async def update(self, id: int, update_data: UserUpdate) -> Optional[User]:
        user = await self.get_by_id(id)
        if not user:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user