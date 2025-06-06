# app/routers/courses.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.database import get_db

router = APIRouter()


@router.get(
    "",
    response_model=List[schemas.CourseResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список всех курсов"
)
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Возвращает список всех курсов (с опциональной пагинацией: skip, limit).
    Если курсов нет — возвращается пустой список.
    """
    courses = crud.get_courses(db, skip=skip, limit=limit)
    return courses


@router.post(
    "",
    response_model=schemas.CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый курс"
)
def create_new_course(course_in: schemas.CourseCreate, db: Session = Depends(get_db)):
    """
    Создаёт новый курс. Проверяет, что указанный teacher_id существует.
    Если преподавателя нет — возвращает 404. При успешном создании — 201.
    """
    new_course = crud.create_course(db, course_in)
    return new_course


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить курс"
)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """
    Удаляет курс по его ID. Если курса с таким ID нет — возвращает 404.
    При успешном удалении — пустой ответ с кодом 204.
    """
    crud.delete_course(db, course_id)
    return None
