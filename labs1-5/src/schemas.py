from pydantic import BaseModel, Field
from typing import Optional, Literal, Any
from datetime import datetime

PriorityType = Literal["Низкий", "Средний", "Высокий", "Критический"]

class ErrorResponse(BaseModel):
    status_code: int = Field(..., description="HTTP-код ошибки", examples=[404])
    error: str = Field(..., description="Краткий тип ошибки", examples=["Not Found"])
    message: str = Field(..., description="Подробное описание ошибки на русском языке", examples=["Заявка с указанным ID не найдена"])
    details: Optional[Any] = Field(None, description="Детали валидации полей (при коде 422)")

class RequestCreate(BaseModel):
    theme: str = Field(
        ...,
        min_length=5,
        max_length=150,
        description="Тема заявки (обязательное поле, от 5 до 150 символов)",
        examples=["Не работает подключение к VPN"]
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Подробное описание проблемы (от 10 до 2000 символов)",
        examples=["При запуске клиента OpenVPN возникает ошибка сертификата."]
    )
    category_id: int = Field(
        ...,
        ge=1,
        le=100,
        description="ID категории заявки (допустимый диапазон: 1–100)",
        examples=[1]
    )
    priority: PriorityType = Field(
        default="Средний",
        description="Приоритет заявки. Допустимые значения: Низкий, Средний, Высокий, Критический",
        examples=["Высокий"]
    )
    status_id: int = Field(
        default=1,
        ge=1,
        le=4,
        description="ID статуса заявки (1 - Новая, 2 - В работе, 3 - Выполнена, 4 - Закрыта)",
        examples=[1]
    )
    applicant_id: int = Field(
        ...,
        ge=1,
        description="ID пользователя-заявителя (целое число >= 1)",
        examples=[1]
    )
    executor_id: Optional[int] = Field(
        default=None,
        ge=1,
        description="ID назначенного исполнителя (опционально, целое число >= 1)",
        examples=[3]
    )
    reg_number: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=20,
        pattern=r"^REQ-\d{3,6}$",
        description="Регистрационный номер в формате REQ-XXX (если не указан, генерируется автоматически)",
        examples=["REQ-011"]
    )

class RequestUpdate(BaseModel):
    theme: Optional[str] = Field(
        None,
        min_length=5,
        max_length=150,
        description="Новое название/тема заявки (от 5 до 150 символов)"
    )
    description: Optional[str] = Field(
        None,
        min_length=10,
        max_length=2000,
        description="Обновленное описание заявки (от 10 до 2000 символов)"
    )
    category_id: Optional[int] = Field(
        None,
        ge=1,
        le=100,
        description="Новый ID категории заявки (диапазон 1–100)"
    )
    priority: Optional[PriorityType] = Field(
        None,
        description="Новый приоритет заявки (Низкий, Средний, Высокий, Критический)"
    )
    status_id: Optional[int] = Field(
        None,
        ge=1,
        le=4,
        description="Новый ID статуса заявки (1 - Новая, 2 - В работе, 3 - Выполнена, 4 - Закрыта)"
    )
    executor_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID назначаемого исполнителя (целое число >= 1)"
    )

class RequestResponse(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор заявки")
    reg_number: Optional[str] = Field(None, description="Регистрационный номер заявки")
    theme: str = Field(..., description="Тема обращения")
    description: str = Field(..., description="Описание проблемы")
    priority: str = Field(..., description="Приоритет выполнения")
    created_at: datetime = Field(..., description="Дата и время регистрации")
    category_id: int = Field(..., description="ID категории")
    status_id: int = Field(..., description="ID текущего статуса")
    applicant_id: int = Field(..., description="ID заявителя")
    executor_id: Optional[int] = Field(None, description="ID назначенного исполнителя")

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int = Field(..., description="ID пользователя")
    full_name: str = Field(..., description="ФИО пользователя")
    role: str = Field(..., description="Роль в системе")

    class Config:
        from_attributes = True

class DictResponse(BaseModel):
    id: int = Field(..., description="ID записи справочника")
    name: str = Field(..., description="Наименование")

    class Config:
        from_attributes = True
