# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# В этом примере используем SQLite-файл university.db.
# При желании, строку подключения можно заменить на другую СУБД (PostgreSQL, MySQL и т.д.).
SQLALCHEMY_DATABASE_URL = "sqlite:///./university.db"

# create_engine с условием check_same_thread=False для SQLite в многопоточном режиме
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Создаём сессию (sessionlocal)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
Base = declarative_base()


# Функция-зависимость для получения сессии в запросах
def get_db():
    """
    Генератор: открывает сессию и корректно её закрывает после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
