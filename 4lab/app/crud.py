# app/crud.py

from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

import app.models as models
import app.schemas as schemas


# ---------------------------
# CRUD для Teacher
# ---------------------------

def get_teacher(db: Session, teacher_id: int) -> Optional[models.Teacher]:
    """
    Получить преподавателя по ID.
    """
    return db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()


def get_teacher_by_name(db: Session, name: str) -> Optional[models.Teacher]:
    """
    Проверка на уникальность имени преподавателя.
    """
    return db.query(models.Teacher).filter(models.Teacher.name == name).first()


def get_teachers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Teacher]:
    """
    Получить список всех преподавателей (с пагинацией).
    """
    return db.query(models.Teacher).offset(skip).limit(limit).all()


def create_teacher(db: Session, teacher_in: schemas.TeacherCreate) -> models.Teacher:
    """
    Создать нового преподавателя. Проверяет уникальность имени.
    """
    existing = get_teacher_by_name(db, teacher_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Преподаватель с именем '{teacher_in.name}' уже существует."
        )
    new_teacher = models.Teacher(name=teacher_in.name)
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


def delete_teacher(db: Session, teacher_id: int) -> None:
    """
    Удалить преподавателя по ID. Если отсутствует — бросить 404.
    Поскольку в модели указан cascade="all, delete-orphan",
    при удалении преподавателя все его курсы удалятся автоматически.
    """
    teacher_obj = get_teacher(db, teacher_id)
    if not teacher_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Преподаватель с id={teacher_id} не найден."
        )
    db.delete(teacher_obj)
    db.commit()


# ---------------------------
# CRUD для Course
# ---------------------------

def get_course(db: Session, course_id: int) -> Optional[models.Course]:
    """
    Получить курс по ID.
    """
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Course]:
    """
    Получить список всех курсов (с пагинацией).
    """
    return db.query(models.Course).offset(skip).limit(limit).all()


def create_course(db: Session, course_in: schemas.CourseCreate) -> models.Course:
    """
    Создать новый курс. Проверить, что преподаватель существует.
    """
    teacher_obj = get_teacher(db, course_in.teacher_id)
    if not teacher_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Преподаватель с id={course_in.teacher_id} не найден."
        )
    new_course = models.Course(
        name=course_in.name,
        student_count=course_in.student_count,
        teacher_id=course_in.teacher_id
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


def delete_course(db: Session, course_id: int) -> None:
    """
    Удалить курс по ID. Если отсутствует — бросить 404.
    """
    course_obj = get_course(db, course_id)
    if not course_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Курс с id={course_id} не найден."
        )
    db.delete(course_obj)
    db.commit()


def get_courses_by_teacher(db: Session, teacher_id: int) -> List[models.Course]:
    """
    Получить все курсы конкретного преподавателя. Если преподавателя нет — 404.
    """
    teacher_obj = get_teacher(db, teacher_id)
    if not teacher_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Преподаватель с id={teacher_id} не найден."
        )
    # Благодаря relationship в модели, можем достать сразу .courses
    return teacher_obj.courses
