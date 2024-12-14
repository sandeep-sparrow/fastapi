from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from TodoApp.db.database import SessionLocal, engine
from TodoApp.models.models import Users
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
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserResponse(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    role: str

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

@router.get("/", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') == 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Cannot access admin details!')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_response = UserResponse(
        username=user_model.username,
        email=user_model.email,
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        role=user_model.role
    )
    return user_response

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None or user.get('user_role') == 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Cannot modify admin password!')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Error on password change')

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
