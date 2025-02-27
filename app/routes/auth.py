from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.security import create_access_token
from app.core.settings import config
from app.repositories.user_repo import UserRepository, get_user_repo
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.utils.response_format import APIResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", response_model=APIResponse, status_code=201)
async def register(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(get_user_repo),
):
    new_user = await user_repo.register_user(user_data)
    print("new_user", new_user)
    return APIResponse(
        message="User created successfully",
        data=UserResponse.model_validate(jsonable_encoder(new_user)),
    )


@router.post("/login", response_model=APIResponse, status_code=200)
async def login(
    user_data: UserLogin,
    user_repo: UserRepository = Depends(get_user_repo),
):
    user = await user_repo.login_user(user_data.username, user_data.password)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=APIResponse(
                message="Incorrect username or password",
                status=401,
                data={},
                error="Incorrect username or password",
            ).model_dump(),
        )

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "version": user.token_version},
        expires_delta=access_token_expires,
    )

    data = {
        "id": user.id,
        "token_type": "bearer",
        "access_token": access_token,
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse(
            message="Login successful",
            status=200,
            data=data,
            error="",
        ).model_dump(),
    )


@router.post("/logout/")
async def logout(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repo),
):
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
        )
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                detail="Could not validate credentials",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = await user_repo.get_user_by_email(email)
        if user is None:
            raise HTTPException(
                detail="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        await user_repo.update_token_version(user.id, increment=True)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=APIResponse(
                message="Successfully logged out",
                status=200,
                data={},
                error="",
            ).model_dump(),
        )
    except JWTError:
        raise HTTPException(
            detail="Invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
