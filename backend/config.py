import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the current backend directory or workspace root
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class Config:
    """Base configuration settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-secret-key-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-dev-jwt-secret-key-change-me")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    PORT = int(os.getenv("PORT", "5000"))

    # CORS configuration
    FRONTEND_URLS_RAW = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8080,http://127.0.0.1:8080,http://localhost:3000"
    )
    CORS_ORIGINS = [url.strip() for url in FRONTEND_URLS_RAW.split(",") if url.strip()]


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    JWT_EXPIRATION_HOURS = 1


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
