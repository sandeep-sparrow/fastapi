from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette import status

from ..db.database import Base
from TodoApp.main import app
from ..endpoints.todos import get_db, get_current_user
from fastapi.testclient import TestClient

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    print("override_get_db called")
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    print("Override for get_current_user called")
    return {"username": "prajapat21", "id": 1, "user_role": "admin"}

# Apply dependency overrides
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_all():
    # for route in app.routes:
    #     print(f"Route: {route.path}, Name: {route.name}, Methods: {route.methods}")
    response = client.get("/todo/")
    print(f"Response status code: {response.status_code}")
    print(f"Response JSON: {response.json()}")
    assert response.status_code == status.HTTP_200_OK




