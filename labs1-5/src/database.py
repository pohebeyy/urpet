import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

os.makedirs("./data", exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/request_system.sqlite3")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

class Status(Base):
    __tablename__ = "statuses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    role = Column(String(50), nullable=False)

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    reg_number = Column(String(20), unique=True, index=True, nullable=True)
    theme = Column(String(150), nullable=False, index=True)
    description = Column(String(2000), nullable=False)
    priority = Column(String(20), nullable=False, default="Средний")
    created_at = Column(DateTime, default=datetime.utcnow)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("statuses.id"), default=1, nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    executor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    category = relationship("Category")
    status = relationship("Status")
    applicant = relationship("User", foreign_keys=[applicant_id])
    executor = relationship("User", foreign_keys=[executor_id])

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String(1000), nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(requests)")).fetchall()]
        if "priority" not in cols:
            conn.execute(text("ALTER TABLE requests ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'Средний'"))
            conn.commit()

    db = SessionLocal()
    try:
        if db.query(Category).count() == 0:
            db.add_all([
                Category(id=1, name="IT-инфраструктура"),
                Category(id=2, name="Хозяйственный отдел"),
                Category(id=3, name="Бухгалтерия"),
                Category(id=4, name="HR"),
            ])
        if db.query(Status).count() == 0:
            db.add_all([
                Status(id=1, name="Новая"),
                Status(id=2, name="В работе"),
                Status(id=3, name="Выполнена"),
                Status(id=4, name="Закрыта"),
            ])
        if db.query(User).count() == 0:
            db.add_all([
                User(id=1, full_name="Иванов И.И.", role="Заявитель"),
                User(id=2, full_name="Смирнова А.", role="Оператор"),
                User(id=3, full_name="Петров П.П.", role="Исполнитель"),
                User(id=4, full_name="Сидоров С.С.", role="Исполнитель"),
                User(id=5, full_name="Админ А.А.", role="Администратор"),
            ])
        db.commit()
        if db.query(Request).count() == 0:
            db.add_all([
                Request(reg_number="REQ-001", theme="Не работает ПК", description="Синий экран смерти при загрузке ОС", priority="Высокий", category_id=1, status_id=1, applicant_id=1, executor_id=None),
                Request(reg_number="REQ-002", theme="Замена офисного стула", description="Сломалась спинка кресла в каб. 101", priority="Низкий", category_id=2, status_id=2, applicant_id=1, executor_id=3),
                Request(reg_number="REQ-003", theme="Выдача справки 2-НДФЛ", description="Нужна срочно справка за 2025 год для банка", priority="Средний", category_id=3, status_id=3, applicant_id=1, executor_id=4),
                Request(reg_number="REQ-004", theme="Доступ в базу 1С", description="Нет прав на проведение документов реализации", priority="Высокий", category_id=1, status_id=4, applicant_id=1, executor_id=3),
                Request(reg_number="REQ-005", theme="Протекает кулер", description="Вода на полу в коридоре на 3 этаже", priority="Критический", category_id=2, status_id=2, applicant_id=1, executor_id=4),
                Request(reg_number="REQ-006", theme="Не печатает сетевой принтер", description="Замятие бумаги в лотке 2 принтера HP", priority="Средний", category_id=1, status_id=1, applicant_id=1, executor_id=None),
                Request(reg_number="REQ-007", theme="Оформление ежегодного отпуска", description="Заявление на отпуск с 15 числа", priority="Низкий", category_id=4, status_id=2, applicant_id=1, executor_id=4),
                Request(reg_number="REQ-008", theme="Замена лампы освещения", description="Перегорела лампа дневного света в каб. 205", priority="Низкий", category_id=2, status_id=3, applicant_id=1, executor_id=3),
                Request(reg_number="REQ-009", theme="Настройка корпоративного VPN", description="Ошибка TLS Handshake при подключении из дома", priority="Критический", category_id=1, status_id=2, applicant_id=1, executor_id=3),
                Request(reg_number="REQ-010", theme="Запрос расчетного листка", description="Не пришел расчетный листок на почту за прошлый месяц", priority="Средний", category_id=3, status_id=4, applicant_id=1, executor_id=4),
            ])
            db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
