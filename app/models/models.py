"""
Модели SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    author = Column(String, nullable=True)
    name = Column(String, nullable=False)
    album = Column(String, nullable=True)
    bitrate = Column(Integer, nullable=True)
    duration_text = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    album_cover_url = Column(String, nullable=True)
    url = Column(String, nullable=False)
    playlist = Column(ForeignKey("playlists.id", ondelete="CASCADE"))


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user = Column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
