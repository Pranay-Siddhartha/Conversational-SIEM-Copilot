import os
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_TITLE: str = "SIEM Copilot API"
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:3001",
    ])
    ENVIRONMENT: str = Field(default="development")

    # Database: sqlite:///data/app.db or environment override
    DATABASE_URL: str = Field(default="")

    # AI Provider: Required for production
    GROQ_API_KEY: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


settings = Settings()
