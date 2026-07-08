"""Configuration management"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "My Agent Core"
    app_version: str = "1.0.0-alpha"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Database
    database_url: str = Field(default="postgresql://user:password@localhost:5432/my_agent")
    mongo_url: str = Field(default="mongodb://localhost:27017/my_agent")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379")

    # Security
    jwt_secret: str = Field(default="your-secret-key-here")
    jwt_expiration_hours: int = 24

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Analysis
    max_file_size_mb: int = 100
    supported_languages: list = [
        "python",
        "javascript",
        "typescript",
        "go",
        "java",
        "cpp",
        "csharp",
        "ruby",
        "php",
        "rust",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
