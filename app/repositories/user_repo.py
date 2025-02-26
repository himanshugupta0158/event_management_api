from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate


async def create_user(db: Session, user_data: UserCreate) -> User:
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        password=get_password_hash(user_data.password),  # Hash password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def get_user_by_username(db: Session, username: str) -> User:
    result = db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: Session, email: str) -> User:
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user(db: Session, user_id: int) -> User:
    result = db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_id(db: Session, user_id: int) -> User:
    result = db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
