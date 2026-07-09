"""Configuration management"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = (PROJECT_ROOT / "backend" / "core" / "my_agent.db").as_posix()


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    # Application
    app_name: str = "My Agent Core"
    app_version: str = "1.0.0-alpha"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Database
    database_url: str = Field(default=f"sqlite+aiosqlite:///{DEFAULT_SQLITE_PATH}")
    mongo_url: str = Field(default="mongodb://localhost:27017/my_agent")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379")

    # Security
    jwt_secret: str = Field(default="my-agent-dev-secret-key-change-in-production-32chars")
    jwt_expiration_hours: int = 24

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # API security
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    allowed_hosts: str = "localhost,127.0.0.1,testserver"

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

settings = Settings()
