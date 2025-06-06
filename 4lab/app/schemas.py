# app/schemas.py

from typing import List, Optional
from pydantic import BaseModel, Field, constr


# ---------------------------
# Схемы для модели Teacher
# ---------------------------

class TeacherBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1) = Field(
        ..., description="ФИО преподавателя"
    )


class TeacherCreate(TeacherBase):
    """
    Схема, используемая при создании нового преподавателя.
    """


class TeacherResponse(BaseModel):
    """
    Схема, возвращаемая клиенту при запросе информации о преподавателе.
    """
    id: int
    name: str

    class Config:
        orm_mode = True


# ---------------------------
# Схемы для модели Course
# ---------------------------

class CourseBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1) = Field(
        ..., description="Название курса"
    )
    student_count: int = Field(
        ..., ge=0, description="Количество студентов на курсе (целое число >= 0)"
    )
    teacher_id: int = Field(
        ..., gt=0, description="Идентификатор преподавателя (должен существовать)"
    )


class CourseCreate(CourseBase):
    """
    Схема, используемая при создании нового курса.
    """


class CourseResponse(BaseModel):
    """
    Схема, возвращаемая клиенту при запросе информации о курсе.
    """
    id: int
    name: str
    student_count: int
    teacher_id: int

    class Config:
        orm_mode = True


class CourseResponseWithTeacher(CourseResponse):
    """
    При необходимости можно расширить.
    Здесь пока тот же, что и CourseResponse.
    """
    pass


# ---------------------------
# Схемы для вложенных ответов
# ---------------------------

class TeacherWithCourses(TeacherResponse):
    courses: List[CourseResponse] = []

    class Config:
        orm_mode = True
