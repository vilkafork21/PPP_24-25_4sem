# app/routers/teachers.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.database import get_db

router = APIRouter()


@router.get(
    "",
    response_model=List[schemas.TeacherResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список всех преподавателей"
)
def read_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Возвращает список всех преподавателей (с опциональной пагинацией: skip, limit).
    Если преподавателей нет — возвращается пустой список.
    """
    teachers = crud.get_teachers(db, skip=skip, limit=limit)
    return teachers


@router.post(
    "",
    response_model=schemas.TeacherResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового преподавателя"
)
def create_new_teacher(teacher_in: schemas.TeacherCreate, db: Session = Depends(get_db)):
    """
    Создаёт нового преподавателя. 
    Если преподаватель с таким именем уже существует — возвращает 400.
    """
    new_teacher = crud.create_teacher(db, teacher_in)
    return new_teacher


@router.get(
    "/{teacher_id}/courses",
    response_model=List[schemas.CourseResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить все курсы преподавателя"
)
def read_courses_by_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """
    Возвращает список курсов, привязанных к преподавателю с заданным teacher_id.
    Если преподавателя с таким ID нет — возвращает 404.
    """
    courses = crud.get_courses_by_teacher(db, teacher_id)
    return courses


@router.delete(
    "/{teacher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить преподавателя (и все его курсы)"
)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """
    Удаляет преподавателя по ID. Если преподавателя нет — возвращает 404.
    При успешном удалении — пустой ответ с кодом 204.
    """
    crud.delete_teacher(db, teacher_id)
    return None
