"""
Health Check Interfaces
"""
from typing import Protocol, Dict, Any, Tuple

class HealthCheck(Protocol):
    """Abstract protocol for defining a health check."""
    
    @property
    def name(self) -> str:
        """Name of the check (e.g., 'database', 'redis')"""
        ...
        
    async def check_health(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Executes the health check.
        Returns (is_healthy, details_dict)
        """
        ...
