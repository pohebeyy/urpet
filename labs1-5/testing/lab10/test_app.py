import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src import database, crud, schemas

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try: yield db
    finally: db.close()

app.dependency_overrides[database.get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_test_db():
    database.Base.metadata.drop_all(bind=engine)
    database.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        db.add_all([database.Category(id=1, name="IT"), database.Status(id=1, name="Новая")])
        db.add_all([database.User(id=1, full_name="Иванов", role="Заявитель")])
        db.commit()
        db.add_all([database.Request(id=1, reg_number="REQ-001", theme="Тема заявки", description="Описание проблемы", priority="Высокий", category_id=1, status_id=1, applicant_id=1)])
        db.commit()
        yield db
    finally:
        db.close()

client = TestClient(app)

def test_api_create_and_get_request_success():
    payload = {"theme": "Установка ПО", "description": "Нужно ПО для работы", "category_id": 1, "priority": "Высокий", "applicant_id": 1}
    resp = client.post("/requests", json=payload)
    assert resp.status_code == 201

def test_api_not_found_missing_resource():
    assert client.get("/requests/9999").status_code == 404

def test_api_bad_request_invalid_foreign_key():
    payload = {"theme": "Тема заявки", "description": "Описание проблемы", "category_id": 99, "priority": "Средний", "applicant_id": 1}
    assert client.post("/requests", json=payload).status_code == 400

def test_validation_empty_patch_body():
    assert client.patch("/requests/1", json={}).status_code == 400

def test_regression_bug02_users_endpoint_available():
    assert client.get("/users").status_code == 200

def test_regression_delete_request():
    assert client.delete("/requests/1").status_code == 204
    assert client.get("/requests/1").status_code == 404