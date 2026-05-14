import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Use a real sqlite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

from src.main import app, get_db
from src.database import Base
from src.models import RoleEnum

# Use a real sqlite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def test_student_signup_and_login():
    # 1. Successful student signup and login, asserting a valid JWT is returned
    signup_data = {
        "name": "Test Student",
        "email": "teststudent@example.com",
        "password": "password123",
        "role": "student"
    }
    response = client.post("/auth/signup", json=signup_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    login_data = {
        "email": "teststudent@example.com",
        "password": "password123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

def test_trainer_creates_session():
    # 2. A trainer creating a session with all required fields
    # First, trainer signup
    trainer_response = client.post("/auth/signup", json={
        "name": "Test Trainer",
        "email": "testtrainer@example.com",
        "password": "password123",
        "role": "trainer"
    })
    trainer_token = trainer_response.json()["access_token"]
    
    # Institution signup
    inst_response = client.post("/auth/signup", json={
        "name": "Test Inst",
        "email": "testinst@example.com",
        "password": "password123",
        "role": "institution"
    })
    inst_token = inst_response.json()["access_token"]

    # Institution creates a batch
    batch_response = client.post("/batches", json={
        "name": "Test Batch",
        "institution_id": 2 # Inst is ID 2
    }, headers={"Authorization": f"Bearer {inst_token}"})
    assert batch_response.status_code == 200
    batch_id = batch_response.json()["id"]

    # Trainer creates session
    session_data = {
        "title": "Intro to Python",
        "date": "2023-10-15",
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "batch_id": batch_id
    }
    session_response = client.post("/sessions", json=session_data, headers={"Authorization": f"Bearer {trainer_token}"})
    assert session_response.status_code == 200
    assert session_response.json()["title"] == "Intro to Python"

def test_student_marking_attendance():
    # 3. A student successfully marking their own attendance
    # Trainer signup
    trainer_res = client.post("/auth/signup", json={
        "name": "Test Trainer",
        "email": "testtrainer@example.com",
        "password": "password123",
        "role": "trainer"
    })
    trainer_token = trainer_res.json()["access_token"]
    
    # Institution signup
    inst_response = client.post("/auth/signup", json={
        "name": "Test Inst",
        "email": "testinst@example.com",
        "password": "password123",
        "role": "institution"
    })
    inst_token = inst_response.json()["access_token"]

    # Institution creates a batch
    batch_res = client.post("/batches", json={
        "name": "Test Batch",
        "institution_id": 2
    }, headers={"Authorization": f"Bearer {inst_token}"})
    batch_id = batch_res.json()["id"]

    # Trainer creates session
    session_res = client.post("/sessions", json={
        "title": "Intro to Python",
        "date": "2023-10-15",
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "batch_id": batch_id
    }, headers={"Authorization": f"Bearer {trainer_token}"})
    session_id = session_res.json()["id"]

    # Trainer generates invite
    invite_res = client.post(f"/batches/{batch_id}/invite", headers={"Authorization": f"Bearer {trainer_token}"})
    invite_token = invite_res.json()["token"]

    # Student signup
    student_res = client.post("/auth/signup", json={
        "name": "Test Student",
        "email": "teststudent@example.com",
        "password": "password123",
        "role": "student"
    })
    student_token = student_res.json()["access_token"]

    # Student joins batch
    join_res = client.post("/batches/join", json={"token": invite_token}, headers={"Authorization": f"Bearer {student_token}"})
    assert join_res.status_code == 200

    # Student marks attendance
    att_res = client.post("/attendance/mark", json={
        "session_id": session_id,
        "status": "present"
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert att_res.status_code == 200
    assert att_res.json()["detail"] == "Attendance marked successfully"

def test_monitoring_attendance_post_method_not_allowed():
    # 4. A POST to /monitoring/attendance returning 405
    response = client.post("/monitoring/attendance")
    assert response.status_code == 405

def test_protected_endpoint_no_token():
    # 5. A request to a protected endpoint with no token returning 401
    response = client.post("/batches", json={
        "name": "Test Batch",
        "institution_id": 1
    })
    assert response.status_code == 401
