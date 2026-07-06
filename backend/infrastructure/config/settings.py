"""
Global Configuration Settings base
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class AppSettings(BaseSettings):
    """
    Base configuration class. Inherits from BaseSettings to automatically 
    load from .env files and environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    env: str = Field(default="development", description="Application environment (dev, staging, prod)")
    debug: bool = Field(default=False, description="Debug mode toggle")
    secret_key: Optional[str] = Field(default=None, description="Global secret key (must be set in prod)")
    
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Logging format")
    project_name: str = Field(default="Swing Trade Bot", description="Project Name")
    version: str = Field(default="0.0.1", description="Project Version")

