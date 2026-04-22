from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.user_service import UserService
from app.utils.jwt import decode_token
from app.models.user import User


class AuthService:
    """Сервис для аутентификации"""
    
    @staticmethod
    def extract_token(request: Request) -> str:
        """Извлекает токен из cookie"""
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        
        if token.startswith("Bearer "):
            token = token[7:]
        return token
    
    @staticmethod
    def validate_token(token: str) -> dict:
        """Проверяет токен и возвращает payload"""
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
        return payload
    
    @staticmethod
    def get_user_id(payload: dict) -> int:
        """Извлекает user_id из payload"""
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token payload")
        return user_id
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Получает пользователя из БД"""
        user_service = UserService(db)
        user = user_service.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
        return user


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Получает текущего пользователя"""
    token = AuthService.extract_token(request)
    payload = AuthService.validate_token(token)
    user_id = AuthService.get_user_id(payload)
    user = AuthService.get_user_by_id(db, user_id)
    
    return user


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверяет права админа"""
    admin_emails = ["admin@school-might.com"]
    
    if current_user.email not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user