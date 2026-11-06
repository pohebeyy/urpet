from fastapi import FastAPI, Depends, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from . import database, schemas, crud

database.init_db()

app = FastAPI(
    title="Request System API — Система учёта заявок",
    description=(
        "Документированный REST API для управления заявками, назначения исполнителей, "
        "контроля статусов и работы со справочниками (Лабораторные работы №6–8)."
    ),
    version="1.0.0"
)

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_names = {
        400: "Bad Request",
        404: "Not Found",
        422: "Unprocessable Entity",
        500: "Internal Server Error"
    }
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "error": error_names.get(exc.status_code, "Error"),
            "message": str(exc.detail),
            "details": None
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": 422,
            "error": "Unprocessable Entity",
            "message": "Ошибка валидации входных параметров запроса",
            "details": exc.errors()
        }
    )

@app.get(
    "/health",
    tags=["System"],
    summary="Проверка работоспособности сервиса (Health Check)",
    description="Возвращает статус доступности API-сервера для мониторинга и Docker healthcheck."
)
def health_check():
    return {"status": "ok", "message": "Приложение работает корректно"}

@app.get(
    "/requests",
    response_model=List[schemas.RequestResponse],
    tags=["Requests"],
    summary="Получение списка заявок с поиском и фильтрацией",
    description=(
        "Возвращает список заявок с поддержкой пагинации (`skip`, `limit`), "
        "контекстного поиска (`search` по регистрационному номеру, теме и описанию), "
        "а также фильтрации по статусу (`status_id`), категории (`category_id`), "
        "приоритету (`priority`) и назначенному исполнителю (`executor_id`)."
    ),
    responses={422: {"model": schemas.ErrorResponse, "description": "Некорректные параметры фильтрации"}}
)
@app.get("/requests/", response_model=List[schemas.RequestResponse], include_in_schema=False)
def read_requests(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей (пагинация)"),
    limit: int = Query(100, ge=1, le=500, description="Максимальное число возвращаемых записей (1–500)"),
    status_id: Optional[int] = Query(None, ge=1, le=4, description="Фильтр по ID статуса (1 - Новая, 2 - В работе, 3 - Выполнена, 4 - Закрыта)"),
    category_id: Optional[int] = Query(None, ge=1, le=100, description="Фильтр по ID категории (1 - IT, 2 - Хозчасть, 3 - Бухгалтерия, 4 - HR)"),
    priority: Optional[schemas.PriorityType] = Query(None, description="Фильтр по приоритету (Низкий, Средний, Высокий, Критический)"),
    executor_id: Optional[int] = Query(None, ge=1, description="Фильтр по ID назначенного исполнителя"),
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Поиск по регистрационному номеру, теме или описанию заявки"),
    db: Session = Depends(database.get_db)
):
    return crud.get_requests(
        db,
        skip=skip,
        limit=limit,
        status_id=status_id,
        category_id=category_id,
        priority=priority,
        executor_id=executor_id,
        search=search
    )

@app.get(
    "/requests/{request_id}",
    response_model=schemas.RequestResponse,
    tags=["Requests"],
    summary="Получение карточки одной заявки по ID",
    description="Возвращает полную информацию о заявке по её уникальному идентификатору.",
    responses={
        404: {"model": schemas.ErrorResponse, "description": "Заявка не найдена"},
        422: {"model": schemas.ErrorResponse, "description": "Некорректный формат ID"}
    }
)
def read_request(request_id: int, db: Session = Depends(database.get_db)):
    db_req = crud.get_request(db, request_id=request_id)
    if db_req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Заявка с id={request_id} не найдена")
    return db_req

@app.post(
    "/requests",
    response_model=schemas.RequestResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Requests"],
    summary="Создание новой заявки",
    description=(
        "Регистрирует новую заявку в системе. Проверяет существование категории, статуса, "
        "заявителя и исполнителя, а также автоматически присваивает регистрационный номер `REQ-XXX`."
    ),
    responses={
        201: {"description": "Заявка успешно создана"},
        400: {"model": schemas.ErrorResponse, "description": "Ошибка бизнес-валидации (несуществующий ID справочника или дубликат номера)"},
        422: {"model": schemas.ErrorResponse, "description": "Ошибка валидации полей схемы RequestCreate"}
    }
)
@app.post("/requests/", response_model=schemas.RequestResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_request(req: schemas.RequestCreate, db: Session = Depends(database.get_db)):
    fk_error = crud.validate_foreign_keys(
        db,
        category_id=req.category_id,
        status_id=req.status_id,
        applicant_id=req.applicant_id,
        executor_id=req.executor_id
    )
    if fk_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=fk_error)
    if req.reg_number and db.query(database.Request).filter_by(reg_number=req.reg_number).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Заявка с номером {req.reg_number} уже существует")
    return crud.create_request(db=db, req=req)

@app.patch(
    "/requests/{request_id}",
    response_model=schemas.RequestResponse,
    tags=["Requests"],
    summary="Частичное изменение заявки (описание, категория, приоритет, статус, исполнитель)",
    description=(
        "Позволяет обновить описание, категорию, приоритет, статус заявки или назначить исполнителя. "
        "Передаются только те поля, которые необходимо изменить."
    ),
    responses={
        200: {"description": "Заявка успешно обновлена"},
        400: {"model": schemas.ErrorResponse, "description": "Пустое тело запроса или несуществующий ID справочника"},
        404: {"model": schemas.ErrorResponse, "description": "Заявка не найдена"},
        422: {"model": schemas.ErrorResponse, "description": "Ошибка валидации полей"}
    }
)
@app.put(
    "/requests/{request_id}",
    response_model=schemas.RequestResponse,
    tags=["Requests"],
    summary="Обновление карточки заявки по ID",
    description="Обновляет поля существующей заявки (тема, описание, категория, приоритет, статус, исполнитель).",
    responses={
        200: {"description": "Заявка успешно обновлена"},
        400: {"model": schemas.ErrorResponse, "description": "Пустое тело запроса или несуществующий ID справочника"},
        404: {"model": schemas.ErrorResponse, "description": "Заявка не найдена"},
        422: {"model": schemas.ErrorResponse, "description": "Ошибка валидации полей"}
    }
)
def update_request(request_id: int, req: schemas.RequestUpdate, db: Session = Depends(database.get_db)):
    update_data = req.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не передано ни одного поля для обновления")
    fk_error = crud.validate_foreign_keys(
        db,
        category_id=req.category_id,
        status_id=req.status_id,
        executor_id=req.executor_id
    )
    if fk_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=fk_error)
    db_req = crud.update_request(db, request_id, req)
    if db_req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Заявка с id={request_id} не найдена")
    return db_req

@app.delete(
    "/requests/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Requests"],
    summary="Удаление заявки по ID",
    description="Удаляет заявку из базы данных по указанному идентификатору. При успехе возвращает HTTP 204 No Content.",
    responses={
        204: {"description": "Заявка успешно удалена"},
        404: {"model": schemas.ErrorResponse, "description": "Заявка не найдена"}
    }
)
def delete_request(request_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_request(db, request_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Заявка с id={request_id} не найдена")
    return None

@app.get(
    "/users",
    response_model=List[schemas.UserResponse],
    tags=["Dictionaries"],
    summary="Получение списка всех пользователей",
    description="Возвращает справочник пользователей системы с указанием ФИО и ролей (Заявитель, Оператор, Исполнитель, Администратор)."
)
@app.get("/users/", response_model=List[schemas.UserResponse], include_in_schema=False)
def get_users(db: Session = Depends(database.get_db)):
    return db.query(database.User).all()

@app.get(
    "/categories",
    response_model=List[schemas.DictResponse],
    tags=["Dictionaries"],
    summary="Получение справочника категорий заявок",
    description="Возвращает список доступных категорий обращений (IT-инфраструктура, Хозяйственный отдел, Бухгалтерия, HR)."
)
@app.get("/categories/", response_model=List[schemas.DictResponse], include_in_schema=False)
def get_categories(db: Session = Depends(database.get_db)):
    return db.query(database.Category).all()

@app.get(
    "/statuses",
    response_model=List[schemas.DictResponse],
    tags=["Dictionaries"],
    summary="Получение справочника статусов заявок",
    description="Возвращает список возможных статусов жизненного цикла заявки (Новая, В работе, Выполнена, Закрыта)."
)
@app.get("/statuses/", response_model=List[schemas.DictResponse], include_in_schema=False)
def get_statuses(db: Session = Depends(database.get_db)):
    return db.query(database.Status).all()
