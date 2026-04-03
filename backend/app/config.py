import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-too")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DB = os.getenv("MYSQL_DB", "incubator_db")
    MYSQL_USER_ENCODED = quote_plus(MYSQL_USER)
    MYSQL_PASSWORD_ENCODED = quote_plus(MYSQL_PASSWORD)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER_ENCODED}:{MYSQL_PASSWORD_ENCODED}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
    AUTO_INIT_DB = os.getenv("AUTO_INIT_DB", "1") == "1"
    SEED_ADMIN_ON_STARTUP = os.getenv("SEED_ADMIN_ON_STARTUP", "0") == "1"
