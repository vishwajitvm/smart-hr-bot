# app/api/users.py

from fastapi import APIRouter
from app.models.user import User, UserCreate
from app.services.user_service import create_user, list_users

router = APIRouter()

@router.post("/", response_model=User)
def create(user: UserCreate):
    return create_user(user)

@router.get("/", response_model=list[User])
def get_all():
    return list_users()
