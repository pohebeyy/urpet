# Система учёта заявок (API & Деплой)

Лабораторные работы №6-8. Разработка функционала, REST API и упаковка в Docker.

## Стек технологий
* **Python 3.12**
* **FastAPI** (Веб-фреймворк)
* **SQLAlchemy** (ORM)
* **Pydantic** (Валидация данных)
* **SQLite** (База данных)
* **Docker & Docker Compose** (Деплой)

## Локальный запуск (Без Docker)
1. Создайте виртуальное окружение: `python -m venv venv`
2. Активируйте: `source venv/bin/activate` (Linux/Mac) или `venv\Scripts\activate` (Windows)
3. Установите зависимости: `pip install -r requirements.txt`
4. Запустите сервер: `uvicorn src.main:app --reload`
5. Документация OpenAPI (Swagger) доступна по адресу: http://localhost:8000/docs

## Запуск в Docker (Деплой)
1. Убедитесь, что установлен Docker и Docker Compose.
2. Выполните команду в корне проекта:
   `docker-compose up -d --build`
3. Контейнер запустится на порту 8000.
4. Health-check: `curl http://localhost:8000/health`
