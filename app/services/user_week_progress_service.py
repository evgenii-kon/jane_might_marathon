from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from app.repositories.user_week_progress_repository import UserWeekProgressRepository
from app.repositories.week_repository import WeekRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.week import Week
from app.services.user_lesson_progress_service import UserLessonProgressService
from app.schemas.user_week_progress import UserWeekProgressResponse, WeekWithProgressResponse


class UserWeekProgressService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserWeekProgressRepository(db)
        self.week_repo = WeekRepository(db)
        self.user_repo = UserRepository(db)


    def _calculate_opens_at(self, user_id: int, week_number: int) -> datetime:
        from datetime import datetime, timedelta, timezone
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, f"User {user_id} not found")
        
        # 🔥 Для первой недели — СЕЙЧАС, а не created_at
        if week_number == 1:
            return datetime.now(timezone.utc)
        
        # Для остальных недель — от created_at
        created_at = user.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        
        return created_at + timedelta(days=(week_number - 1) * 7)


    def get_or_create(self, user_id: int, week_id: int) -> UserWeekProgressResponse:
        """Получить или создать прогресс для недели"""
        progress = self.repository.get_by_user_and_week(user_id, week_id)
        
        if not progress:
            week = self.week_repo.get_by_id(week_id)
            if not week:
                raise HTTPException(404, f"Week {week_id} not found")
            
            opens_at = self._calculate_opens_at(user_id, week.number)
            progress = self.repository.create(user_id, week_id, opens_at)
        
        return UserWeekProgressResponse.model_validate(progress)


    def init_user_weeks(self, user_id: int) -> None:
        """
        Инициализировать прогресс для всех недель при регистрации
        Вызывается один раз при создании пользователя
        """
        weeks = self.week_repo.get_all()
        
        weeks_opens_at = []
        for week in weeks:
            opens_at = self._calculate_opens_at(user_id, week.number)
            weeks_opens_at.append((week.id, opens_at))
        
        self.repository.create_many(user_id, weeks_opens_at)


    def is_week_available(self, user_id: int, week_id: int) -> bool:
        """Проверить, доступна ли неделя пользователю сейчас"""
        progress = self.repository.get_by_user_and_week(user_id, week_id)
        if not progress:
            return False
        
        now = datetime.now(timezone.utc)
        return now >= progress.opens_at


    def mark_week_completed(self, user_id: int, week_id: int) -> UserWeekProgressResponse:
        """Отметить неделю как пройденную"""
        progress = self.repository.mark_completed(user_id, week_id)
        if not progress:
            raise HTTPException(404, f"Progress not found for user {user_id}, week {week_id}")
        
        return UserWeekProgressResponse.model_validate(progress)


    from datetime import datetime, timezone

    def get_weeks_with_progress(self, user_id: int) -> List[WeekWithProgressResponse]:
        """
        Получить все недели с прогрессом пользователя
        Для отображения на дашборде
        """
        from app.services.user_lesson_progress_service import UserLessonProgressService
        
        weeks = self.week_repo.get_all()
        lesson_progress_service = UserLessonProgressService(self.db)
        now = datetime.now(timezone.utc)
        
        result = []
        for week in weeks:
            # Получаем прогресс пользователя по этой неделе
            user_progress = self.repository.get_by_user_and_week(user_id, week.id)
            
            if user_progress:
                opens_at = user_progress.opens_at
                # Приводим к UTC если нужно
                if opens_at.tzinfo is None:
                    opens_at = opens_at.replace(tzinfo=timezone.utc)
                
                is_locked = now < opens_at
                is_completed = user_progress.is_completed
                
                # 🔥 ДОБАВИТЬ ЭТУ СТРОКУ
                days_until_open = (opens_at - now).days + 1 if is_locked else None
                
            else:
                # Если записи нет, создаём
                opens_at = self._calculate_opens_at(user_id, week.number)
                is_locked = now < opens_at
                is_completed = False
                
                # 🔥 ДОБАВИТЬ ЭТУ СТРОКУ
                days_until_open = (opens_at - now).days + 1 if is_locked else None
            
            # Получаем прогресс по урокам в неделе
            lesson_progress = lesson_progress_service.get_week_progress(user_id, week.id)
            
            result.append(WeekWithProgressResponse(
                id=week.id,
                number=week.number,
                name=week.name,
                short_description=week.short_description,
                long_description=week.long_description,
                is_locked=is_locked,
                is_completed=is_completed,
                opens_at=opens_at,
                days_until_open=days_until_open,  # 🔥 ДОБАВИТЬ ЭТУ СТРОКУ
                completed_lessons=lesson_progress.completed,
                total_lessons=lesson_progress.total,
                progress_percent=lesson_progress.progress_percent
            ))
        
        return result