from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    gemini_api_key: str
    app_name: str = "Forex Chart Analyzer"
    debug: bool = True
    default_risk_percent: float = 1.0
    max_file_size: int = 10485760
    
    class Config:
        env_file = ".env"

settings = Settings()
