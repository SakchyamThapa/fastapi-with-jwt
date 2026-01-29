from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    
    # Admin credentials
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    
    class Config:
        env_file = ".env"

settings = Settings()
