from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.article import Article
from ..schemas.article import ArticleCreate, ArticleUpdate


class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_all(self) -> List[Article]:
        """Получить все статьи"""
        return self.db.query(Article).order_by(Article.created_at.desc()).all()


    def get_by_id(self, article_id: int) -> Optional[Article]:
        """Получить статью по ID"""
        return self.db.query(Article).filter(Article.id == article_id).first()


    def get_by_slug(self, slug: str) -> Optional[Article]:
        """Получить статью по slug"""
        return self.db.query(Article).filter(Article.slug == slug).first()


    def create(self, article_data: ArticleCreate) -> Article:
        """Создать новую статью"""
        new_article = Article(**article_data.model_dump())
        self.db.add(new_article)
        self.db.commit()
        self.db.refresh(new_article)
        return new_article


    def update(self, article_id: int, update_data: dict) -> Optional[Article]:
        """Обновить статью"""
        article = self.get_by_id(article_id)
        if not article:
            return None
        
        for key, value in update_data.items():
            setattr(article, key, value)
        
        self.db.commit()
        self.db.refresh(article)
        return article


    def delete(self, article_id: int) -> bool:
        """Удалить статью"""
        article = self.get_by_id(article_id)
        if not article:
            return False
        
        self.db.delete(article)
        self.db.commit()
        return True

    
    def count(self) -> int:
        """Получить количество статей"""
        return self.db.query(Article).count()