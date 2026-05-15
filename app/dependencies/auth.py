from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.user_service import UserService
from app.utils.jwt import decode_token
from app.models.user import User


class AuthService:
    """Сервис для аутентификации"""
    
    @staticmethod
    def extract_token(request: Request) -> str:
        """Извлекает токен из cookie (обязательный режим)"""
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        
        if token.startswith("Bearer "):
            token = token[7:]
        return token
    
    
    @staticmethod
    def extract_token_optional(request: Request) -> Optional[str]:
        """Извлекает токен из cookie (опциональный режим)"""
        token = request.cookies.get("access_token")
        if not token:
            return None
        
        if token.startswith("Bearer "):
            token = token[7:]
        return token
    

    @staticmethod
    def validate_token(token: str) -> dict:
        """Проверяет токен и возвращает payload (обязательный режим)"""
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
        return payload
    

    @staticmethod
    def validate_token_optional(token: Optional[str]) -> Optional[dict]:
        """Проверяет токен и возвращает payload (опциональный режим)"""
        if not token:
            return None
        payload = decode_token(token)
        if not payload:
            return None
        return payload
    

    @staticmethod
    def get_user_id(payload: dict) -> int:
        """Извлекает user_id из payload (обязательный режим)"""
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token payload")
        return user_id
    

    @staticmethod
    def get_user_id_optional(payload: Optional[dict]) -> Optional[int]:
        """Извлекает user_id из payload (опциональный режим)"""
        if not payload:
            return None
        user_id = payload.get("user_id")
        return user_id


    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Получает пользователя из БД (обязательный режим)"""
        user_service = UserService(db)
        user = user_service.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
        return user
    

    @staticmethod
    def get_user_by_id_optional(db: Session, user_id: Optional[int]) -> Optional[User]:
        """Получает пользователя из БД (опциональный режим)"""
        if not user_id:
            return None
        user_service = UserService(db)
        user = user_service.repository.get_by_id(user_id)
        return user


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Получает текущего пользователя (обязательная авторизация)"""
    token = AuthService.extract_token(request)
    payload = AuthService.validate_token(token)
    user_id = AuthService.get_user_id(payload)
    user = AuthService.get_user_by_id(db, user_id)
    
    return user


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Получает текущего пользователя, если авторизован, иначе None (опциональная авторизация)"""
    token = AuthService.extract_token_optional(request)
    if not token:
        return None
    
    payload = AuthService.validate_token_optional(token)
    if not payload:
        return None
    
    user_id = AuthService.get_user_id_optional(payload)
    if not user_id:
        return None
    
    user = AuthService.get_user_by_id_optional(db, user_id)
    return user


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверяет права админа"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user