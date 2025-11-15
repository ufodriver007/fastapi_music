"""
Модели(схемы) Pydantic для валидации
"""
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """
    Модель для создания и обновления пользователя.
    Используется в POST и PUT запросах.
    """
    username: str = Field(min_length=3, max_length=25, description="Логин пользователя")
    password: str = Field(min_length=8, description="Пароль пользователя (минимум 8 символов)")
    email: EmailStr = Field(description="E-mail пользователя")


class User(BaseModel):
    """
    Модель для ответа с данными пользователя.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор пользователя")
    username: str = Field(min_length=3, max_length=25, description="Логин пользователя")
    password: str = Field(min_length=8, description="Пароль пользователя (минимум 8 символов)")
    email: EmailStr = Field(description="E-mail пользователя")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания пользователя")

    model_config = ConfigDict(from_attributes=True)


class Song(BaseModel):
    id: int = Field(description="Уникальный идентификатор песни")
    author: Optional[str] = Field(None, description="Автор песни")
    name: str = Field(description="Название песни")
    album: Optional[str] = Field(None, description="Альбом")
    bitrate: Optional[int] = Field(None, description="Битрейт")
    duration_text: str = Field(description="Длительность в виде текста")
    duration: int = Field(description="Длительность в секундах")
    album_cover_url: Optional[str] = Field(None, max_length=200, description="URL изображения альбома")
    url: str = Field(max_length=200, description="URL песни")
    playlist_id: int = Field(description="ID плейлиста")

    # это позволяет преобразовывать объекты SQLAlchemy в Pydantic-модели для ответа
    model_config = ConfigDict(from_attributes=True)


class SongCreate(BaseModel):
    author: Optional[str] = Field(None, description="Автор песни")
    name: str = Field(description="Название песни")
    album: Optional[str] = Field(None, description="Альбом")
    bitrate: Optional[int] = Field(None, description="Битрейт")
    duration_text: str = Field(description="Длительность в виде текста")
    duration: int = Field(description="Длительность в секундах")
    album_cover_url: Optional[str] = Field(None, max_length=200, description="URL изображения альбома")
    url: str = Field(max_length=200, description="URL песни")
    playlist_id: int = Field(description="ID плейлиста")


class PlaylistCreate(BaseModel):
    """
    Модель для создания и обновления плейлиста.
    Используется в POST и PUT запросах.
    """
    name: str = Field(description="Название плейлиста")
    description: Optional[str] = Field(None, description="Описание плейлиста")


class Playlist(BaseModel):
    """
    Модель для ответа с данными плейлиста.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор плейлиста")
    name: str = Field(description="Название плейлиста")
    description: Optional[str] = Field(None, description="Описание плейлиста")
    user_id: int = Field(description="ID пользователя")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания плейлиста")

    # это позволяет преобразовывать объекты SQLAlchemy в Pydantic-модели для ответа
    model_config = ConfigDict(from_attributes=True)

