from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.core.settings import config
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            password=get_password_hash(user_data.password),
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    async def get_user_by_username(self, username: str) -> User:
        result = self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User:
        result = self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user(self, user_id: int) -> User:
        result = self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def register_user(self, user_data: UserCreate) -> User:
        existing_user = await self.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        return await self.create_user(user_data)

    async def login_user(self, identifier: str, password: str) -> User:
        user = (
            await self.get_user_by_email(identifier)
            if "@" in identifier
            else await self.get_user_by_username(identifier)
        )

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return user

    async def logout_user(self, token: str) -> None:
        try:
            payload = jwt.decode(
                token,
                config.SECRET_KEY,
                algorithms=[config.ALGORITHM],
            )
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not validate credentials",
                )

            user = await self.get_user(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            user.token_version += 1
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    async def update_token_version(self, user_id: int, increment: bool = True) -> User:
        user = await self.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if increment:
            user.token_version += 1
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


def get_user_repo(db: Session = Depends(get_db)):
    return UserRepository(db)
