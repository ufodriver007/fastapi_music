import os
from dotenv import load_dotenv


load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")
DB_HOST = os.getenv("DB_HOST")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
HOST = os.getenv("HOST")
CACHE_TTL = int(os.getenv("CACHE_TTL"))
THROTTLING_LIMIT = int(os.getenv("THROTTLING_LIMIT"))
THROTTLING_LIMIT_TIME = int(os.getenv("THROTTLING_LIMIT_TIME"))
