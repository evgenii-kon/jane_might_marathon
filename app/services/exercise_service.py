import json
import re
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import status, HTTPException
from ..repositories.exercise_repository import ExerciseRepository
from ..schemas.exercise import (
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseResponse,
    ExerciseCheckResponse,
)
from ..services.cashe_service import CacheService

_TRANSLATE_PUNCT_RE = re.compile(r"[，,。.！!？?；;：:、\s]+")


def _normalize_translate_answer(text: str) -> str:
    """Сравнение ответов в 'translate' игнорирует регистр и знаки препинания
    (пользователь не обязан ставить точку/запятую так же, как в эталоне)."""
    return _TRANSLATE_PUNCT_RE.sub("", text.strip().lower())


class ExerciseService:
    def __init__(self, db: AsyncSession):
        self.repository = ExerciseRepository(db)
        self.cache = CacheService(prefix='exercise', ttl = 300)

    async def get_all_exercises(self) -> List[ExerciseResponse]:
        """Получить все упражнения"""
        cached = await self.cache.get('all')
        if cached:
            return [ExerciseResponse.model_validate(e) for e in cached]
        
        exercises = await self.repository.get_all()
        result = [ExerciseResponse.model_validate(e) for e in exercises]
        await self.cache.set([e.model_dump(mode='json') for e in result], 'all') 
        return result

    async def get_exercise_by_id(self, exercise_id: int) -> ExerciseResponse:
        """Получить упражнение по ID"""
        cached = await self.cache.get('id', exercise_id)
        if cached:
            return ExerciseResponse.model_validate(cached)
        
        exercise = await self.repository.get_by_id(exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id={exercise_id} not found",
            )
        result = ExerciseResponse.model_validate(exercise)
        await self.cache.set(result.model_dump(mode='json'), 'id', exercise_id)
        return result

    async def get_exercises_by_lesson(self, lesson_id: int) -> List[ExerciseResponse]:
        """Получить все упражнения урока (отсортированные)"""
        cached = await self.cache.get('lesson', lesson_id)
        if cached:
            return [ExerciseResponse.model_validate(e) for e in cached]
        exercises = await self.repository.get_by_lesson(lesson_id)

        result = [ExerciseResponse.model_validate(e) for e in exercises]
        await self.cache.set([e.model_dump(mode='json') for e in result], 'lesson', lesson_id)
        return result

    async def create_exercise(self, exercise_data: ExerciseCreate) -> ExerciseResponse:
        """Создать новое упражнение"""
        await self.cache.delete_pattern('*')
        new_exercise = await self.repository.create(exercise_data)

        return ExerciseResponse.model_validate(new_exercise)

    async def update_exercise(
        self, exercise_id: int, exercise_data: ExerciseUpdate
    ) -> ExerciseResponse:
        """Обновить упражнение"""
        exercise_exist_check = await self.repository.get_by_id(exercise_id)
        if not exercise_exist_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id={exercise_id} not found",
            )
        
        await self.cache.delete_pattern('*')

        update_dict = exercise_data.model_dump(exclude_unset=True)
        exercise = await self.repository.update(exercise_id, update_dict)

        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id={exercise_id} not found",
            )

        return ExerciseResponse.model_validate(exercise)

    async def delete_exercise(self, exercise_id: int) -> bool:
        """Удалить упражнение"""
        exercise_exist_check = await self.repository.get_by_id(exercise_id)
        if not exercise_exist_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id={exercise_id} not found",
            )
        await self.cache.delete_pattern('*')
        return await self.repository.delete(exercise_id)

    async def get_exercises_count_by_lesson(self, lesson_id: int) -> int:
        """Получить количество упражнений в уроке"""
        cached = await self.cache.get('lessons_count', lesson_id)
        if cached:
            return cached
        result = await self.repository.get_count_by_lesson(lesson_id)
        await self.cache.set(result, 'lessons_count', lesson_id)
        return result

    async def check_answer(
        self,
        exercise_id: int,
        selected_option: int | None = None,
        user_answer: str | None = None,
        pairs: list[dict] | None = None,
    ) -> ExerciseCheckResponse:
        """Проверить ответ пользователя (логика зависит от exercise.type)"""
        exercise = await self.repository.get_by_id(exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id={exercise_id} not found",
            )

        config = exercise.config or {}

        if exercise.type in ("quiz", "choose_hanzi", "fill_blank", "audio_quiz"):
            options = config.get("options", [])
            correct = config.get("correct")
            is_correct = selected_option == correct

            def option_text(index):
                if index is None or index < 0 or index >= len(options):
                    return ""
                return options[index]

            return ExerciseCheckResponse(
                is_correct=is_correct,
                correct_answer=correct,
                explanation=exercise.explanation if not is_correct else None,
                user_answer=option_text(selected_option),
                correct_answer_text=option_text(correct),
            )

        if exercise.type == "matching_pairs":
            # Пары проверяются на клиенте по мере кликов; здесь просто
            # отмечаем факт завершения раунда.
            return ExerciseCheckResponse(is_correct=True)

        if exercise.type == "build_word":
            answer = config.get("answer", "")
            is_correct = user_answer == answer
            return ExerciseCheckResponse(
                is_correct=is_correct,
                correct_answer=answer,
                explanation=exercise.explanation if not is_correct else None,
                user_answer=user_answer,
                correct_answer_text=answer,
            )

        if exercise.type == "translate":
            answer = config.get("answer", "")
            is_correct = _normalize_translate_answer(user_answer or "") == _normalize_translate_answer(answer)
            return ExerciseCheckResponse(
                is_correct=is_correct,
                correct_answer=answer,
                explanation=exercise.explanation if not is_correct else None,
                user_answer=user_answer,
                correct_answer_text=answer,
            )

        if exercise.type == "multi_select":
            statements = config.get("statements", [])
            correct = sorted(config.get("correct", []))
            try:
                selected = sorted(set(json.loads(user_answer or "[]")))
            except (TypeError, ValueError):
                selected = []
            is_correct = selected == correct
            correct_answer_text = " · ".join(statements[i] for i in correct if 0 <= i < len(statements))
            return ExerciseCheckResponse(
                is_correct=is_correct,
                explanation=exercise.explanation if not is_correct else None,
                user_answer=user_answer,
                correct_answer_text=correct_answer_text,
            )

        if exercise.type == "fill_blank_open":
            blanks = config.get("blanks", [])
            try:
                user_blanks = json.loads(user_answer or "[]")
            except (TypeError, ValueError):
                user_blanks = []
            is_correct = len(user_blanks) == len(blanks) and all(
                (u or "").strip().lower() == (b or "").strip().lower()
                for u, b in zip(user_blanks, blanks)
            )
            correct_answer_text = " · ".join(b if b else "(пусто)" for b in blanks)
            return ExerciseCheckResponse(
                is_correct=is_correct,
                explanation=exercise.explanation if not is_correct else None,
                user_answer=user_answer,
                correct_answer_text=correct_answer_text,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown exercise type: {exercise.type}",
        )
