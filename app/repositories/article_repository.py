from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from ..models.article import Article
from ..schemas.article import ArticleCreate

class ArticleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Article]:
        """Получить все статьи"""
        result = await self.db.execute(
            select(Article).order_by(Article.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, article_id: int) -> Optional[Article]:
        """Получить статью по ID"""
        result = await self.db.execute(
            select(Article).where(Article.id == article_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Article]:
        """Получить статью по slug"""
        result = await self.db.execute(
            select(Article).where(Article.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create(self, article_data: ArticleCreate) -> Article:
        """Создать новую статью"""
        new_article = Article(**article_data.model_dump())
        self.db.add(new_article)
        await self.db.commit()
        await self.db.refresh(new_article)
        return new_article

    async def update(self, article_id: int, update_data: dict) -> Optional[Article]:
        """Обновить статью"""
        article = await self.get_by_id(article_id)
        if not article:
            return None
        for key, value in update_data.items():
            setattr(article, key, value)
        await self.db.commit()
        await self.db.refresh(article)
        return article

    async def delete(self, article_id: int) -> bool:
        """Удалить статью"""
        article = await self.get_by_id(article_id)
        if not article:
            return False
        await self.db.delete(article)
        await self.db.commit()
        return True

    async def count(self) -> int:
        """Получить количество статей"""
        result = await self.db.execute(select(func.count()).select_from(Article))
        return result.scalar_one()