from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.services.user_service import UserService
from app.services.week_service import WeekService
from app.services.lesson_service import LessonService
from app.services.user_lesson_progress_service import UserLessonProgressService


router = APIRouter(prefix='/dashboard/weeks', tags = ['dashboard'])
templates = Jinja2Templates(directory='app/templates')

@router.get('/{week_id}', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def week_detail(
    request: Request,
    week_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    week_service = WeekService(db)
    lesson_service = LessonService(db)
    progress_service = UserLessonProgressService(db)

    try:
        week = week_service.get_week_by_id(week_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'week with id={week_id} not found'
            )
    
    lessons = lesson_service.get_lessons_by_week(week_id)
    completed_ids = progress_service.get_completed_lesson_ids(current_user.id)
    started_ids = progress_service.get_started_lesson_ids(current_user.id)


    lessons_data = []
    for lesson in lessons:
        lessons_data.append({
            'id': lesson.id,
            'name': lesson.name,
            'order_in_week': lesson.order_in_week,
            'description': getattr(lesson, 'description', None),
            'is_completed': lesson.id in completed_ids,
            'is_started': lesson.id in started_ids
        })
    
    # Прогресс по неделе
    completed_count = len([l for l in lessons_data if l['is_completed']])
    progress_percent = int((completed_count / len(lessons_data)) * 100) if lessons_data else 0
    
    
    return templates.TemplateResponse('dashboard/weeks/week_detail.html', {
        'request': request,
        'week': week,
        'lessons': lessons_data,
        'completed_count': completed_count,
        'total_count': len(lessons),
        'progress_percent': progress_percent,
        'user': current_user
    })

