"""
Database Configuration
Extends the core application settings with database-specific configurations.
"""
from pydantic import Field
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """Database specific configurations."""
    
    # Driver and connection
    db_driver: str = Field(default="sqlite+aiosqlite", description="Database driver (e.g., postgresql+asyncpg)")
    db_host: str = Field(default="", description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_user: str = Field(default="", description="Database user")
    db_password: str = Field(default="", description="Database password")
    db_name: str = Field(default="swing_bot.db", description="Database name")
    
    # Connection pooling
    db_pool_size: int = Field(default=20, description="Connection pool size")
    db_max_overflow: int = Field(default=10, description="Max overflow connections")
    db_pool_timeout: int = Field(default=30, description="Pool timeout in seconds")
    db_pool_recycle: int = Field(default=1800, description="Pool recycle time in seconds")
    db_echo: bool = Field(default=False, description="Echo SQL statements (for debugging)")

    def get_database_url(self) -> str:
        """Constructs the SQLAlchemy connection URL."""
        if "sqlite" in self.db_driver:
            # SQLite specific formatting
            return f"{self.db_driver}:///{self.db_name}"
        
        # Standard PostgreSQL/MySQL formatting
        return f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

db_settings = DatabaseSettings()
