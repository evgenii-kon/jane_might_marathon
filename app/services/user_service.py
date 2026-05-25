from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserResponse, UserUpdate
from fastapi import HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, email: str, password: str):
        """Аутентификация пользователя"""
        user = await self.repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not self.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return user

    async def get_all_users(self) -> List[UserResponse]:
        users = await self.repository.get_all()
        return [UserResponse.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user with id={user_id} not found",
            )
        return UserResponse.model_validate(user)

    async def get_user_by_email(self, user_email: str) -> UserResponse:
        user = await self.repository.get_by_email(user_email)
        if not user:
            raise HTTPException(
                status=status.HTTP_404_NOT_FOUND,
                detail=f"user with email {user_email} not found",
            )
        return UserResponse.model_validate(user)

    async def get_user_by_name(self, user_name: str) -> UserResponse:
        user = await self.repository.get_by_name(user_name)
        if not user:
            raise HTTPException(
                status=status.HTTP_404_NOT_FOUND,
                detail=f"user with name {user_name} not found",
            )
        return UserResponse.model_validate(user)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        user_exist_check = await self.repository.get_by_email(user_data.email)
        if user_exist_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"user with email {user_data.email} is already exist",
            )
        data_dict = user_data.model_dump()
        password_hash = self._hash_password(data_dict.pop("password"))
        data_dict["password_hash"] = password_hash
        user = await self.repository.create(data_dict)
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> bool:
        result = await self.repository.delete(user_id)
        return result

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        update_dict = user_data.model_dump(exclude_unset=True)
        if "password" in update_dict and update_dict["password"] is not None:
            password_hash = self._hash_password(update_dict.pop("password"))
            update_dict["password_hash"] = password_hash
        else:
            update_dict.pop("password", None)
        user = await self.repository.update(user_id, update_dict)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user with id={user_id} not found",
            )
        return UserResponse.model_validate(user)