from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from ..repositories.article_repository import ArticleRepository
from ..schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse


class ArticleService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ArticleRepository(db)


    def get_all_articles(self) -> List[ArticleResponse]:
        """Получить все статьи"""
        articles = self.repository.get_all()
        return [ArticleResponse.model_validate(a) for a in articles]


    def get_article_by_id(self, article_id: int) -> ArticleResponse:
        """Получить статью по ID"""
        article = self.repository.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with id={article_id} not found"
            )
        return ArticleResponse.model_validate(article)


    def get_article_by_slug(self, slug: str) -> ArticleResponse:
        """Получить статью по slug"""
        article = self.repository.get_by_slug(slug)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with slug='{slug}' not found"
            )
        return ArticleResponse.model_validate(article)


    def create_article(self, article_data: ArticleCreate) -> ArticleResponse:
        """Создать новую статью"""
        # Проверяем уникальность slug
        existing = self.repository.get_by_slug(article_data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Article with slug='{article_data.slug}' already exists"
            )
        
        new_article = self.repository.create(article_data)
        return ArticleResponse.model_validate(new_article)


    def update_article(self, article_id: int, article_data: ArticleUpdate) -> ArticleResponse:
        """Обновить статью"""
        article = self.repository.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with id={article_id} not found"
            )
        
        # Если меняется slug, проверяем уникальность
        if article_data.slug and article_data.slug != article.slug:
            existing = self.repository.get_by_slug(article_data.slug)
            if existing and existing.id != article_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Article with slug='{article_data.slug}' already exists"
                )
        
        update_dict = article_data.model_dump(exclude_unset=True)
        updated_article = self.repository.update(article_id, update_dict)
        return ArticleResponse.model_validate(updated_article)


    def delete_article(self, article_id: int) -> None:
        """Удалить статью"""
        article = self.repository.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with id={article_id} not found"
            )
        
        self.repository.delete(article_id)


    def get_articles_count(self) -> int:
        """Получить количество статей"""
        return self.repository.count()