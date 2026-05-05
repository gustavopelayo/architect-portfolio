try:
    # Try to import from pydantic_settings (pydantic v2+)
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback to pydantic v1
    from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Architect Portfolio"
    SECRET_KEY: str = "your-secret-key-here"  # Should be loaded from env in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./test.db"  # Using SQLite for simplicity
    
    class Config:
        case_sensitive = True

settings = Settings()