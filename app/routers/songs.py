from fastapi import APIRouter, Body, Depends, HTTPException, status
from app.models.models import Song as SongModel, Playlist, User as UserModel
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from auth import hash_password, verify_password, create_access_token, create_refresh_token, get_current_user
from db_depends import get_async_db
from schemas import SongCreate


router = APIRouter(prefix='/songs', tags=['Песни', ])


@router.get('')
async def get_all_user_songs(db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_user)
                           ):
    """All user's songs"""
    stmt = select(Playlist).where(Playlist.user == current_user.id)
    playlists = (await db.execute(stmt)).scalars().all()

    result = []
    for playlist in playlists:
        songs = (await db.execute(select(SongModel).where(SongModel.playlist == playlist.id))).scalars().all()
        for song in songs:
            result.append(song)

    return result


@router.get('/{song_id}')
async def get_song(song_id: int,
                   db: AsyncSession = Depends(get_async_db),
                   current_user: UserModel = Depends(get_current_user)
                   ):
    """Get song by id"""
    # Проверяем существование песни
    stmt = select(SongModel).where(SongModel.id == song_id)
    song = (await db.execute(stmt)).scalar_one_or_none()

    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")


    return song


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_song(song_data: SongCreate,
                      db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_user)
                      ):
    """Create a new song"""
    # Проверяем, есть ли у данного пользователя такой плейлист
    stmt = select(Playlist).where(Playlist.id == song_data.playlist_id, Playlist.user == current_user.id)
    playlist = (await db.execute(stmt)).scalar_one_or_none()

    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found or does not belong to the user")

    db_item = SongModel(name=song_data.name,
                   duration_text=song_data.duration_text,
                   duration=song_data.duration,
                   url=song_data.url,
                   author=song_data.author,
                   album=song_data.album,
                   bitrate=song_data.bitrate,
                   album_cover_url=song_data.album_cover_url,
                   playlist=song_data.playlist_id
                   )

    # добавляет объект в сессию
    db.add(db_item)

    # фиксирует все изменения, сделанные в текущей сессии (выполняет запрос к БД)
    await db.commit()

    # обновляет состояние объекта db_item из базы данных
    await db.refresh(db_item)

    return db_item


@router.patch('/{song_id}')
async def rename_song(song_id: int,
                      name: str,
                      db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_user)
                      ):
    """Rename song by id"""
    # Проверяем существование песни
    stmt = select(SongModel).where(SongModel.id == song_id)
    song = (await db.execute(stmt)).scalar_one_or_none()

    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")

    song.name = name

    # фиксирует все изменения, сделанные в текущей сессии (выполняет запрос к БД)
    await db.commit()
    # обновляет состояние объекта db_item из базы данных
    await db.refresh(song)

    return song


@router.delete('/{song_id}')
async def delete_song(song_id: int,
                   db: AsyncSession = Depends(get_async_db),
                   current_user: UserModel = Depends(get_current_user)
                   ):
    """Get song by id"""
    # Проверяем существование песни
    stmt = select(SongModel).where(SongModel.id == song_id)
    song = (await db.execute(stmt)).scalar_one_or_none()

    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")

    await db.delete(song)
    await db.commit()
    return {'deleted': 'Song deleted'}
