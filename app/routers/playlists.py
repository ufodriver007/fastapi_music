from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db_depends import get_async_db
from app.models.models import User as UserModel, Playlist, Song
from auth import hash_password, verify_password, create_access_token, create_refresh_token, get_current_user


router = APIRouter(prefix='/playlists', tags=['Плейлисты', ])


@router.get('')
async def get_user_playlists(db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_user)
                           ):
    """All user's playlists"""
    stmt = select(Playlist).where(Playlist.user == current_user.id)
    playlists = (await db.execute(stmt)).scalars().all()
    return playlists


@router.get('/{playlist_id}')
async def get_playlist(playlist_id: int,
                       db: AsyncSession = Depends(get_async_db),
                       current_user: UserModel = Depends(get_current_user)
                       ):
    """Get playlist and it songs by id"""
    # Проверяем существование плейлиста и принадлежность пользователю
    stmt = select(Playlist).where(and_(Playlist.id == playlist_id, Playlist.user == current_user.id))
    playlist = (await db.execute(stmt)).scalar_one_or_none()

    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    # Находим все песни этого плейлиста
    stmt = select(Song).where(Song.playlist == playlist_id)
    songs = (await db.execute(stmt)).scalars().all()

    return {
        "playlist": {
            "id": playlist.id,
            "name": playlist.name,
        },
        "songs": songs if songs else []
    }


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_playlist(name: str = Body(embed=True),
                          db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_user)):
    """Create a new playlist"""
    db_item = Playlist(name=name, user=current_user.id)

    # добавляет объект в сессию
    db.add(db_item)

    # фиксирует все изменения, сделанные в текущей сессии (выполняет запрос к БД)
    await db.commit()

    # обновляет состояние объекта db_item из базы данных
    await db.refresh(db_item)

    return db_item


@router.patch('/{playlist_id}')
async def rename_playlist(playlist_id: int,
                          name: str,
                          db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_user)
                          ):
    """Rename playlist by id"""
    # Проверяем существование плейлиста и принадлежность пользователю
    stmt = select(Playlist).where(and_(Playlist.id == playlist_id, Playlist.user == current_user.id))
    playlist = (await db.execute(stmt)).scalar_one_or_none()

    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    playlist.name = name

    # фиксирует все изменения, сделанные в текущей сессии (выполняет запрос к БД)
    await db.commit()
    # обновляет состояние объекта db_item из базы данных
    await db.refresh(playlist)

    return playlist



@router.delete('/{playlist_id}')
async def delete_playlist(playlist_id: int,
                          db: AsyncSession = Depends(get_async_db),
                          current_user: UserModel = Depends(get_current_user)
                          ):
    """Delete playlist by id"""
    # Проверяем существование плейлиста и принадлежность пользователю
    stmt = select(Playlist).where(and_(Playlist.id == playlist_id, Playlist.user == current_user.id))
    playlist = (await db.execute(stmt)).scalar_one_or_none()

    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    await db.delete(playlist)
    # фиксирует все изменения, сделанные в текущей сессии (выполняет запрос к БД)
    await db.commit()
    return {'deleted': 'Playlist deleted'}


# @router.post('/add-song')
# async def add_song_to_playlist(playlist_id: int = Body(embed=True), song_id: int = Body(embed=True)):
#     return await PlaylistDAO.add_song_to_playlist(playlist_id, song_id)
#
#
# @router.post('/remove-song')
# async def remove_song_from_playlist(playlist_id: int = Body(embed=True), song_id: int = Body(embed=True)):
#     return await PlaylistDAO.remove_song_from_playlist(playlist_id, song_id)

