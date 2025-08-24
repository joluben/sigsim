"""
Application configuration settings
"""
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/app.db"
    
    # CORS
    cors_origins: Union[List[str], str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    # Simulation limits
    max_devices_per_project: int = 1000
    max_concurrent_projects: int = 10
    
    # Performance
    connection_pool_size: int = 100
    request_timeout: int = 30
    
    @field_validator('cors_origins')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"


settings = Settings()