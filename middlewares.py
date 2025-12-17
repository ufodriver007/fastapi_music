import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis
from loguru import logger
import config


class TimingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        start_time = time.time()
        await self.app(scope, receive, send)
        duration = time.time() - start_time
        print(f"Request duration: {duration:.10f} seconds")


class ThrottlingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        redis_client: redis.Redis,
        limit: int,
        window_seconds: int,
        allowed_origin: str = None,
    ):
        super().__init__(app)
        self.redis = redis_client
        self.limit = limit
        self.window = window_seconds
        self.allowed_origin = allowed_origin  # нужен для CORS

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        client_ip = request.client.host
        key = f"throttle:{client_ip}"

        # увеличение счётчика у ключа (по достижении порога TTL ключ сам удалится)
        current = await self.redis.incr(key)

        # при первом вызове устанавливем TTL у ключа
        if current == 1:
            await self.redis.expire(key, self.window)

        if current > self.limit:
            response = JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )
            # CORS заголовки, чтобы fetch с credentials видел ответ
            if self.allowed_origin:
                response.headers["Access-Control-Allow-Origin"] = self.allowed_origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

        response = await call_next(request)
        return response

