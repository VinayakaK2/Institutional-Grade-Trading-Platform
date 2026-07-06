"""
Health Check Manager
Aggregates health status from registered dependencies (DB, Redis, etc.)
"""
import asyncio
from typing import List, Dict, Any, cast
from backend.infrastructure.health.checks import HealthCheck
from backend.core.logger import get_logger

logger = get_logger(__name__)

class HealthCheckManager:
    """Manages and aggregates health checks."""
    
    def __init__(self):
        self._checks: List[HealthCheck] = []
        
    def register(self, check: HealthCheck) -> None:
        """Registers a new health check component."""
        self._checks.append(check)
        logger.debug(f"Registered health check: {check.name}")
        
    async def get_health_report(self) -> Dict[str, Any]:
        """
        Executes all registered health checks concurrently and aggregates the report.
        """
        report = {
            "status": "healthy",
            "components": {}
        }
        
        if not self._checks:
            return report
            
        tasks = [check.check_health() for check in self._checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for check, result in zip(self._checks, results):
            component_name = check.name
            if isinstance(result, Exception):
                logger.error(f"Health check failed for {component_name}", exc_info=result)
                report["status"] = "unhealthy"
                # type ignore is fine here due to dynamic dict structure in python
                report["components"][component_name] = { # type: ignore
                    "status": "unhealthy",
                    "error": str(result)
                }
            else:
                is_healthy, details = cast(tuple, result)
                report["components"][component_name] = { # type: ignore
                    "status": "healthy" if is_healthy else "unhealthy",
                    "details": details
                }
                if not is_healthy:
                    report["status"] = "unhealthy"
                    
        return report

# Global Health Manager
health_manager = HealthCheckManager()
