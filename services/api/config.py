"""Application Configuration Module.

This module manages all configuration settings for the Color Correction System API.
It uses Pydantic BaseSettings for type-safe environment variable management with
validation and default values.

Supports multiple environments:
- Development (SQLite, debug mode)
- Testing (In-memory SQLite)
- Production (PostgreSQL, optimized settings)

Usage:
    from config import settings
    print(settings.DATABASE_URL)
    print(settings.SECRET_KEY)
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, validator, Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support.
    
    All settings can be overridden via environment variables.
    Environment variables should be prefixed with APP_ (configurable via Config.env_prefix).
    
    Attributes:
        APP_NAME: Application name
        APP_VERSION: API version
        DEBUG: Debug mode flag
        ENVIRONMENT: Current environment (dev/test/prod)
        SECRET_KEY: JWT secret key for token generation
        ALGORITHM: JWT algorithm
        ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time
        DATABASE_URL: SQLAlchemy database connection string
        MAX_UPLOAD_SIZE: Maximum file upload size in bytes
        ALLOWED_EXTENSIONS: List of allowed file extensions
        CELERY_BROKER_URL: Redis/RabbitMQ URL for Celery
        CELERY_RESULT_BACKEND: Result backend for Celery tasks
        CORS_ORIGINS: List of allowed CORS origins
        LOG_LEVEL: Logging level
    """
    
    # Application Settings
    APP_NAME: str = "Color Correction API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Security Settings
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-this-in-production-please-use-openssl-rand-hex-32",
        env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="sqlite:///./color_correction.db",
        env="DATABASE_URL"
    )
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = Field(
        default=50 * 1024 * 1024,  # 50 MB
        env="MAX_UPLOAD_SIZE"
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "tiff", "tif", "raw", "dng", "cr2", "nef"],
        env="ALLOWED_EXTENSIONS"
    )
    UPLOAD_DIRECTORY: str = Field(default="./uploads", env="UPLOAD_DIRECTORY")
    
    # Celery Settings (for background tasks)
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_RESULT_BACKEND"
    )
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",  # Next.js dev server
            "http://localhost:8000",  # FastAPI dev server
            "http://localhost",
        ],
        env="CORS_ORIGINS"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # ArUco Detection Settings
    ARUCO_DICT: str = Field(default="DICT_4X4_50", env="ARUCO_DICT")
    MIN_MARKER_AREA: int = Field(default=100, env="MIN_MARKER_AREA")
    
    # Color Correction Settings
    DEFAULT_COLOR_SPACE: str = Field(default="sRGB", env="DEFAULT_COLOR_SPACE")
    MAX_DELTA_E: float = Field(default=10.0, env="MAX_DELTA_E")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str) -> str:
        """Validate and format database URL.
        
        Args:
            v: Database URL string
            
        Returns:
            Validated database URL
            
        Raises:
            ValueError: If database URL is invalid
        """
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        
        # Handle Heroku postgres:// URLs by converting to postgresql://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str, values: dict) -> str:
        """Validate secret key in production.
        
        Args:
            v: Secret key value
            values: Other validated values
            
        Returns:
            Validated secret key
            
        Raises:
            ValueError: If using default secret key in production
        """
        if values.get("ENVIRONMENT") == "production":
            if "change-this" in v.lower() or "super-secret" in v.lower():
                raise ValueError(
                    "You must set a secure SECRET_KEY in production. "
                    "Generate one with: openssl rand -hex 32"
                )
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list.
        
        Args:
            v: CORS origins (string or list)
            
        Returns:
            List of CORS origin strings
        """
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_allowed_extensions(cls, v):
        """Parse allowed extensions from string or list.
        
        Args:
            v: Allowed extensions (string or list)
            
        Returns:
            List of allowed extension strings
        """
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        return [ext.lower() for ext in v]
    
    def is_production(self) -> bool:
        """Check if running in production environment.
        
        Returns:
            True if environment is production
        """
        return self.ENVIRONMENT.lower() in ["production", "prod"]
    
    def is_development(self) -> bool:
        """Check if running in development environment.
        
        Returns:
            True if environment is development
        """
        return self.ENVIRONMENT.lower() in ["development", "dev"]
    
    def is_testing(self) -> bool:
        """Check if running in testing environment.
        
        Returns:
            True if environment is testing
        """
        return self.ENVIRONMENT.lower() in ["testing", "test"]
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Uses LRU cache to ensure settings are only loaded once.
    Call this function to access settings throughout the application.
    
    Returns:
        Settings instance with all configuration
        
    Example:
        >>> from config import get_settings
        >>> settings = get_settings()
        >>> print(settings.DATABASE_URL)
    """
    return Settings()


# Global settings instance
settings = get_settings()
