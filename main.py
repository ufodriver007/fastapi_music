import os
from loguru import logger
from fastapi import FastAPI, Query, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

import config
from app.routers import playlists, songs, users
from utils import vk_search, mail_ru_search
from auth import get_current_user
from app.models.models import User as UserModel
import httpx
from utils import ExternalServiceError
from middlewares import ThrottlingMiddleware
from redis_cache import redis_client
from redis_cache import make_cache_key, cache_set, cache_get


logger.add('logs/main.log', rotation='10mb', level='DEBUG')

app = FastAPI(
    title="Music service",
    version="0.1.0",
)

client = httpx.AsyncClient(timeout=10.0)

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
app.add_middleware(
    ThrottlingMiddleware,
    redis_client=redis_client,
    limit=config.THROTTLING_LIMIT,
    window_seconds=config.THROTTLING_LIMIT_TIME,
    allowed_origin = origins[0]
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
                 current_user: UserModel = Depends(get_current_user)
                 ):
    logger.debug(f"query={q}; mail.ru={mailru};")

    key: str = make_cache_key(q, mcount, 'mailru' if mailru else 'default')
    cached = await cache_get(key)  # list[dict] | None

    if cached is not None:
        return cached

    if mailru:
        try:
            items = await mail_ru_search(client, q, count=mcount)
            await cache_set(key, items)
            return items
        except ExternalServiceError as e:
            raise HTTPException(status_code=502, detail=str(e))



@app.get("/health", summary="Healthcheck", description="Проверка работоспособности сервиса")
async def healthcheck():
    return {"status": "ok"}
