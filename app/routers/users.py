import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from app.models.models import User as UserModel
from schemas import UserCreate, User as UserSchema
from db_depends import get_async_db
from auth import hash_password, verify_password, create_access_token, create_refresh_token, get_current_user
from config import SECRET_KEY, ALGORITHM
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, PyJWTError


router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.post('', response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя
    """
    # Проверка уникальности email
    result = await db.scalars(select(UserModel).where(UserModel.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered")

    # Проверка уникальности username
    result = await db.scalars(select(UserModel).where(UserModel.username == user.username))
    if result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already registered")

    # Создание объекта пользователя с хешированным паролем
    db_user = UserModel(
        username=user.username,
        email=str(user.email),
        password=hash_password(user.password)
    )

    # Добавление в сессию и сохранение в базе
    db.add(db_user)
    await db.commit()
    return db_user


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_db)):
    """
    Аутентифицирует пользователя и возвращает access_token и refresh_token
    """
    result = await db.scalars(select(UserModel).where(UserModel.email == form_data.username))
    user = result.first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email, "id": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_async_db)):
    """  
    Обновляет access_token с помощью refresh_token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except (ExpiredSignatureError, InvalidTokenError, PyJWTError):
        raise credentials_exception
    result = await db.scalars(select(UserModel).where(UserModel.email == email, UserModel.is_active == True))
    user = result.first()
    if user is None:
        raise credentials_exception
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """
    Получает информацию о текущем пользователе
    """
    return current_user
