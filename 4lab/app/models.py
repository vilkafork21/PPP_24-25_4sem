# app/models.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    # Связь 1:M с курсами
    courses = relationship(
        "Course",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    student_count = Column(Integer, nullable=False, default=0)

    # Внешний ключ на таблицу teachers
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)

    # Обратная связь
    teacher = relationship("Teacher", back_populates="courses")
