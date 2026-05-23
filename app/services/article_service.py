from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException, status
from ..repositories.article_repository import ArticleRepository
from ..schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse


class ArticleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ArticleRepository(db)

    async def get_all_articles(self) -> List[ArticleResponse]:
        """Получить все статьи"""
        articles = await self.repository.get_all()
        return [ArticleResponse.model_validate(a) for a in articles]

    async def get_article_by_id(self, article_id: int) -> ArticleResponse:
        """Получить статью по ID"""
        article = await self.repository.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with id={article_id} not found",
            )
        return ArticleResponse.model_validate(article)

    async def get_article_by_slug(self, slug: str) -> ArticleResponse:
        """Получить статью по slug"""
        article = await self.repository.get_by_slug(slug)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with slug='{slug}' not found",
            )
        return ArticleResponse.model_validate(article)

    async def create_article(self, article_data: ArticleCreate) -> ArticleResponse:
        """Создать новую статью"""
        # Проверяем уникальность slug
        existing = await self.repository.get_by_slug(article_data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Article with slug='{article_data.slug}' already exists",
            )

        new_article = await self.repository.create(article_data)
        return ArticleResponse.model_validate(new_article)

    async def update_article(
        self, article_id: int, article_data: ArticleUpdate
    ) -> ArticleResponse:
        """Обновить статью"""
        article = await self.repository.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with id={article_id} not found",
            )

        # Если меняется slug, проверяем уникальность
        if article_data.slug and article_data.slug != article.slug:
            existing = await self.repository.get_by_slug(article_data.slug)
            if existing and existing.id != article_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Article with slug='{article_data.slug}' already exists",
                )

        update_dict = article_data.model_dump(exclude_unset=True)
        updated_article = await self.repository.update(article_id, update_dict)
        return ArticleResponse.model_validate(updated_article)

    async def delete_article(self, article_id: int) -> None:
        """Удалить статью"""
        article = await self.repository.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with id={article_id} not found",
            )

        await self.repository.delete(article_id)

    async def get_articles_count(self) -> int:
        """Получить количество статей"""
        result = await self.repository.count()
        return result
