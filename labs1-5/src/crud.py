from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from . import database, schemas

def get_request(db: Session, request_id: int):
    return db.query(database.Request).filter(database.Request.id == request_id).first()

def get_requests(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status_id: Optional[int] = None,
    category_id: Optional[int] = None,
    priority: Optional[str] = None,
    executor_id: Optional[int] = None,
    search: Optional[str] = None
):
    query = db.query(database.Request)
    if status_id is not None:
        query = query.filter(database.Request.status_id == status_id)
    if category_id is not None:
        query = query.filter(database.Request.category_id == category_id)
    if priority is not None:
        query = query.filter(database.Request.priority == priority)
    if executor_id is not None:
        query = query.filter(database.Request.executor_id == executor_id)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                database.Request.reg_number.ilike(pattern),
                database.Request.theme.ilike(pattern),
                database.Request.description.ilike(pattern)
            )
        )
    return query.offset(skip).limit(limit).all()

def validate_foreign_keys(
    db: Session,
    category_id: Optional[int] = None,
    status_id: Optional[int] = None,
    applicant_id: Optional[int] = None,
    executor_id: Optional[int] = None
):
    if category_id is not None and not db.query(database.Category).filter_by(id=category_id).first():
        return f"Категория с id={category_id} не существует"
    if status_id is not None and not db.query(database.Status).filter_by(id=status_id).first():
        return f"Статус с id={status_id} не существует"
    if applicant_id is not None and not db.query(database.User).filter_by(id=applicant_id).first():
        return f"Заявитель с id={applicant_id} не существует"
    if executor_id is not None and not db.query(database.User).filter_by(id=executor_id).first():
        return f"Исполнитель с id={executor_id} не существует"
    return None

def create_request(db: Session, req: schemas.RequestCreate):
    db_req = database.Request(**req.model_dump())
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    if not db_req.reg_number:
        db_req.reg_number = f"REQ-{db_req.id:03d}"
        db.commit()
        db.refresh(db_req)
    return db_req

def update_request(db: Session, request_id: int, req_update: schemas.RequestUpdate):
    db_req = get_request(db, request_id)
    if not db_req:
        return None
    update_data = req_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_req, key, value)
    db.commit()
    db.refresh(db_req)
    return db_req

def delete_request(db: Session, request_id: int):
    db_req = get_request(db, request_id)
    if db_req:
        db.delete(db_req)
        db.commit()
        return True
    return False
