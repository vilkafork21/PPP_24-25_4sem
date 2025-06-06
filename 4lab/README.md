
```markdown
# University API

Простое FastAPI-приложение для управления преподавателями и курсами (вариант №2).

## Структура проекта

```

university\_api/
├── app/
│   ├── **init**.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── routers/
│   │   ├── **init**.py
│   │   ├── teachers.py
│   │   └── courses.py
│   └── utils.py            (может быть пустым или отсутствовать)
├── requirements.txt
├── README.md
└── university.db           (создаётся при первом запуске)

````

## Как запустить

1. Склонировать репозиторий или скопировать файлы в папку `university_api`.
2. Перейти в папку проекта:
   ```bash
   cd university_api
````

3. Создать и активировать виртуальное окружение (рекомендуется):

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # на Linux/macOS
   venv\Scripts\activate.bat     # на Windows
   ```

4. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   ```

5. Запустить приложение:

   ```bash
   uvicorn app.main:app --reload
   ```

   Это поднимет сервер на `http://127.0.0.1:8000`.

6. Проверить, что всё работает:

   * Откройте в браузере `http://127.0.0.1:8000/ping` → должно вернуть `{"status": "ok"}`.
   * Автоматическая документация (Swagger UI) будет доступна по адресу `http://127.0.0.1:8000/docs`.

## Описание эндпоинтов

### Преподаватели

* `GET /teachers`
  → возвращает список всех преподавателей.
* `POST /teachers`
  Тело (JSON):

  ```json
  {
    "name": "Иванов И.И."
  }
  ```

  → создаёт нового преподавателя, отвечает `{ "id": ..., "name": "..." }`.
* `GET /teachers/{teacher_id}/courses`
  → список всех курсов данного преподавателя.
* `DELETE /teachers/{teacher_id}`
  → удаляет преподавателя и все его курсы (каскадно).

### Курсы

* `GET /courses`
  → возвращает список всех курсов.
* `POST /courses`
  Тело (JSON):

  ```json
  {
    "name": "Математический анализ",
    "student_count": 25,
    "teacher_id": 1
  }
  ```

  → создаёт курс, отвечает `{ "id": ..., "name": "...", "student_count": ..., "teacher_id": ... }`.
* `DELETE /courses/{course_id}`
  → удаляет курс по ID.

Все ответы и ошибки приходят в формате JSON, коды статусов (200, 201, 204, 400, 404 и т.д.) соответствуют API-контракту.

---

### Что делать дальше

1. **Проверьте, что у вас в папке лежат все файлы**:

   * `app/main.py`
   * `app/database.py`
   * `app/models.py`
   * `app/schemas.py`
   * `app/crud.py`
   * `app/routers/teachers.py`
   * `app/routers/courses.py`
   * `app/utils.py` (пусть будет пустым или не существует)
   * `requirements.txt`
   * `README.md`

2. **Установите зависимости** командой:

   ```bash
   pip install -r requirements.txt
   ```

3. **Запустите сервер**:

   ```bash
   uvicorn app.main:app --reload
   ```

   и убедитесь, что:

   * `GET http://127.0.0.1:8000/ping` возвращает `{"status":"ok"}`.
   * Swagger UI (`http://127.0.0.1:8000/docs`) показывает все четыре эндпоинта для `/teachers` и три для `/courses`.

Если всё заработало — проект готов. При необходимости можно добавить:

* **Тесты** в папку `tests/` (например, с `pytest`).
* **Миграции** через Alembic (если вы планируете развивать БД дальше).
* Логику для `utils.py` (если появятся общие утилиты).

Но по минимальным требованиям данная структура и код уже полностью закрывают описанный API.
