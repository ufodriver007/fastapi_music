from loguru import logger
from fastapi import FastAPI, Query, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Optional
from app.routers import playlists, songs, users
from utils import vk_search, mail_ru_search
from auth import get_current_user
from app.models.models import User as UserModel


logger.add('logs/main.log', rotation='10mb', level='DEBUG')

app = FastAPI(
    title="Music service",
    version="0.1.0",
)

origins = ["http://localhost:5173",
           "http://127.0.0.1:5173"
           ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(playlists.router)
app.include_router(songs.router)
app.include_router(users.router)


@app.get('/')
async def home():
    return {'detail': 'Modern music API. See /search?q=Rammtein'}


@app.get('/search')
async def search(q: str,
                 mailru: Optional[bool] = True,
                 mcount: int = Query(100, gt=0, le=300),
                 vk: Optional[bool] = True,
                 vcount: int = Query(100, gt=0, le=300),
                 current_user: UserModel = Depends(get_current_user)
                 ):
    logger.debug(f"query={q}; mail.ru={mailru}; vk={vk}")


    if mailru and vk:
        mailru_songs = mail_ru_search(q)
        vk_songs = vk_search(q)
        return {'mailru': mailru_songs, 'vk': vk_songs}

    if mailru:
        mailru_songs = mail_ru_search(q, count=mcount)
        return mailru_songs

    if vk:
        vk_songs = vk_search(q, count=vcount)
        return vk_songs

