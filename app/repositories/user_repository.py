from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.user import User
from ..schemas.user import UserCreate
from ..database import get_db


class UserRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_all(self) -> List[User]:
        return self.db.query(User).all()
    

    def get_by_id(self, id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id==id).first()


    def get_by_name(self, name: str) -> Optional[User]:
        return self.db.query(User).filter(User.name == name).first()
    

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    

    def create(self, data: dict) -> User:
        """передается data: dict а не pydantic модель для того чтобы захешировать пароль"""
        new_user = User(**data)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
    
    def delete(self, id: int) -> bool:
        user = self.db.query(User).filter(User.id == id).first()
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        else: return False

