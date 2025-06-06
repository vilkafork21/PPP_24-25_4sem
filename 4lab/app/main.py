# app/main.py

from fastapi import FastAPI
from app.database import engine, Base
from app.routers import teachers, courses

# Создаём объект приложения
app = FastAPI(title="University API", version="1.0")

# При запуске приложения убедимся, что все таблицы созданы
Base.metadata.create_all(bind=engine)

# Регистрируем роутеры
app.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
app.include_router(courses.router, prefix="/courses", tags=["courses"])


@app.get("/ping", summary="Проверочный эндпоинт")
def ping():
    """
    Возвращает простой ответ для проверки работоспособности API.
    """
    return {"status": "ok"}
