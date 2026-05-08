from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import status, HTTPException
from ..repositories.exercise_repository import ExerciseRepository
from ..schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseResponse, ExerciseCheckRequest, ExerciseCheckResponse
from ..models.exercise import Exercise


class ExerciseService:
    def __init__(self, db: Session):
        self.repository = ExerciseRepository(db)


    def get_all_exercises(self) -> List[ExerciseResponse]:
        """Получить все упражнения"""
        exercises = self.repository.get_all()
        return [ExerciseResponse.model_validate(e) for e in exercises]


    def get_exercise_by_id(self, exercise_id: int) -> ExerciseResponse:
        """Получить упражнение по ID"""
        exercise = self.repository.get_by_id(exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Exercise with id={exercise_id} not found'
            )
        return ExerciseResponse.model_validate(exercise)


    def get_exercises_by_lesson(self, lesson_id: int) -> List[ExerciseResponse]:
        """Получить все упражнения урока (отсортированные)"""
        exercises = self.repository.get_by_lesson(lesson_id)
        return [ExerciseResponse.model_validate(e) for e in exercises]


    def create_exercise(self, exercise_data: ExerciseCreate) -> ExerciseResponse:
        """Создать новое упражнение"""
        # Проверяем, существует ли урок с таким ID (опционально)
        # lesson_service = LessonService(self.db)
        # lesson_service.get_lesson_by_id(exercise_data.lesson_id)
        
        new_exercise = self.repository.create(exercise_data)
        return ExerciseResponse.model_validate(new_exercise)


    def update_exercise(self, exercise_id: int, exercise_data: ExerciseUpdate) -> ExerciseResponse:
        """Обновить упражнение"""
        exercise_exist_check = self.repository.get_by_id(exercise_id)
        if not exercise_exist_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Exercise with id={exercise_id} not found'
            )
        
        update_dict = exercise_data.model_dump(exclude_unset=True)
        exercise = self.repository.update(exercise_id, update_dict)
        
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Exercise with id={exercise_id} not found'
            )
        
        return ExerciseResponse.model_validate(exercise)


    def delete_exercise(self, exercise_id: int) -> bool:
        """Удалить упражнение"""
        exercise_exist_check = self.repository.get_by_id(exercise_id)
        if not exercise_exist_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Exercise with id={exercise_id} not found'
            )
        
        return self.repository.delete(exercise_id)


    def get_exercises_count_by_lesson(self, lesson_id: int) -> int:
        """Получить количество упражнений в уроке"""
        return self.repository.get_count_by_lesson(lesson_id)


    def check_answer(self, exercise_id: int, selected_option: int) -> ExerciseCheckResponse:
        """Проверить ответ пользователя"""
        exercise = self.repository.get_by_id(exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Exercise with id={exercise_id} not found'
            )
        
        is_correct = (selected_option == exercise.correct_answer)
        
        # Получаем текст выбранного варианта
        option_map = {
            1: exercise.option_1,
            2: exercise.option_2,
            3: exercise.option_3,
            4: exercise.option_4,
        }
        
        correct_option_map = {
            1: exercise.option_1,
            2: exercise.option_2,
            3: exercise.option_3,
            4: exercise.option_4,
        }
        
        return ExerciseCheckResponse(
            is_correct=is_correct,
            correct_answer=exercise.correct_answer,
            explanation=exercise.explanation if not is_correct else None,
            user_answer=option_map.get(selected_option, ""),
            correct_answer_text=correct_option_map.get(exercise.correct_answer, "")
        )