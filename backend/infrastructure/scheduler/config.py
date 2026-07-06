"""
Scheduler Configuration
"""
from pydantic import Field
from pydantic_settings import BaseSettings

class SchedulerSettings(BaseSettings):
    """Scheduler specific configurations."""
    
    scheduler_timezone: str = Field(default="UTC", description="Default timezone for scheduled jobs")
    scheduler_max_instances: int = Field(default=3, description="Max concurrent instances of a single job")
    scheduler_misfire_grace_time: int = Field(default=60, description="Grace time (seconds) for misfired jobs")
    scheduler_coalesce: bool = Field(default=True, description="Coalesce missed job executions into one")

scheduler_settings = SchedulerSettings()
