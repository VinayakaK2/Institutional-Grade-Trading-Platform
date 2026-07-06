"""
Integration Tests for Health Check Framework
"""
import pytest
from backend.infrastructure.health.manager import HealthCheckManager

class MockHealthyCheck:
    @property
    def name(self): return "mock_healthy"
    async def check_health(self): return True, {"uptime": "100s"}

class MockUnhealthyCheck:
    @property
    def name(self): return "mock_unhealthy"
    async def check_health(self): return False, {"error": "connection timeout"}

@pytest.mark.asyncio
async def test_health_manager_aggregation():
    manager = HealthCheckManager()
    manager.register(MockHealthyCheck())
    manager.register(MockUnhealthyCheck())
    
    report = await manager.get_health_report()
    
    assert report["status"] == "unhealthy"
    assert report["components"]["mock_healthy"]["status"] == "healthy"
    assert report["components"]["mock_unhealthy"]["status"] == "unhealthy"
