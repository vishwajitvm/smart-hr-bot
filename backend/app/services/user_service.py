# app/services/user_service.py

from app.models.user import User, UserCreate

_fake_users: list[User] = []

def create_user(user: UserCreate) -> User:
    new_user = User(id=len(_fake_users) + 1, **user.dict())
    _fake_users.append(new_user)
    return new_user

def list_users() -> list[User]:
    return _fake_users
