import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..main import app
from ..database import Base
from ..routers.todos import get_db, get_current_user
from fastapi.testclient import TestClient
import pytest
from fastapi import status
from ..models import Todos

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

@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1,
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

def test_read_all_authenticated(test_todo):
    # for route in app.routes:
    #     print(f"Route: {route.path}, Name: {route.name}, Methods: {route.methods}")
    response = client.get("/todo/")
    print(f"Response status code: {response.status_code}")
    print(f"Response JSON: {response.json()}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False,
                                'description': 'Need to learn everyday!',
                                'id': 1,
                                'owner_id': 1,
                                'priority': 5,
                                'title': 'Learn to code!'}]

def test_read_one_authenticated(test_todo):
    # for route in app.routes:
    #     print(f"Route: {route.path}, Name: {route.name}, Methods: {route.methods}")
    response = client.get("/todo/1")
    print(f"Response status code: {response.status_code}")
    print(f"Response JSON: {response.json()}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False,
                                'description': 'Need to learn everyday!',
                                'id': 1,
                                'owner_id': 1,
                                'priority': 5,
                                'title': 'Learn to code!'}

def test_read_one_authenticated_not_found():
    # for route in app.routes:
    #     print(f"Route: {route.path}, Name: {route.name}, Methods: {route.methods}")
    response = client.get("/todo/2")
    print(f"Response status code: {response.status_code}")
    print(f"Response JSON: {response.json()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found!'}

def test_create_todo(test_todo):
    request_data = {
        'title': 'New todo!',
        'description': 'New Todo Description!',
        'priority': 5,
        'complete': False,
    }
    response = client.post('/todo', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')