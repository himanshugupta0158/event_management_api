from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.core.settings import config
from app.repositories.user_repo import create_user, get_user_by_id, get_user_by_username
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.utils.response_format import APIResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", response_model=APIResponse, status_code=201)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = await create_user(db, user_data)
    return APIResponse(
        message="User created successfully",
        data=UserResponse(new_user),
    )


@router.post("/login", response_model=APIResponse, status_code=200)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = await get_user_by_username(db, user_data.username)
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  # We store user.id in the 'sub'
        expires_delta=access_token_expires,
    )
    return APIResponse(
        message="User logged in successfully",
        data={"access_token": access_token, "token_type": "bearer"},
    )


@router.post("/logout", response_model=APIResponse, status_code=200)
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Decode the token
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

        # Retrieve the user and increment their token version
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.token_version += 1  # Invalidate existing tokens by bumping version
        db.add(user)
        db.commit()
        db.refresh(user)

        return APIResponse(
            message="Successfully logged out",
            data={},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
