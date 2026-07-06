"""
Redis Configuration
Extends the core application settings with Redis-specific configurations.
"""
from pydantic import Field
from pydantic_settings import BaseSettings

class RedisSettings(BaseSettings):
    """Redis specific configurations."""
    
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_max_connections: int = Field(default=100, description="Maximum number of connections in the pool")
    redis_timeout: int = Field(default=5, description="Socket timeout in seconds")
    redis_retry_on_timeout: bool = Field(default=True, description="Retry on timeout flag")
    
    # Global Cache Strategy
    redis_default_ttl: int = Field(default=3600, description="Default Time-To-Live for cache keys in seconds (1 hour)")
    redis_key_prefix: str = Field(default="swingbot:", description="Global prefix for all Redis keys to avoid collision")

redis_settings = RedisSettings()
