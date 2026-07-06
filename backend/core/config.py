"""
Configuration Foundation (Phase 0)
Provides a strongly-typed, environment-aware configuration architecture.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AppSettings(BaseSettings):
    """
    Core application settings.
    This serves as the root configuration object. All specific modules 
    (Database, Logging, Broker) should have their own isolated settings classes 
    if they become complex, which can be composed into this one.
    """
    
    # Environment identification
    env: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Global logging level")
    log_format: str = Field(default="json", description="Log format: json or text")

    # Project Information
    project_name: str = Field(default="Institutional Swing Trading Platform", description="Project Name")
    version: str = Field(default="0.0.1-alpha", description="Project Version")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# Global settings instance
settings = AppSettings()
