import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./fitness_app.db"
    
    # Google AI API
    GOOGLE_API_KEY: str
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App Settings
    APP_NAME: str = "Fitness AI Backend"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
