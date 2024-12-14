from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from starlette import status
from TodoApp.db.database import SessionLocal, engine
from TodoApp.models.models import Todos
from TodoApp import models
from .auth import get_current_user

router = APIRouter()

models.models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get("/{todo_id}")
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    todo_model = (db.query(Todos)
                  .filter(Todos.id == todo_id)
                  .filter(Todos.owner_id == user.get('id'))
                  .first())
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found!')

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TodoRequest)
async def create_todo(db: db_dependency,
                      user: user_dependency,
                      todo_request: TodoRequest):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')


    todo_model = Todos(**todo_request.dict(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()

    return todo_model

@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,
                      user: user_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    todo_model = (db.query(Todos)
                  .filter(Todos.id == todo_id)
                  .filter(Todos.owner_id == user.get('id'))
                  .first())
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found!")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    todo_model = (db.query(Todos)
                  .filter(Todos.id == todo_id)
                  .first())
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found!")

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    db.commit()