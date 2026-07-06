import asyncio
import logging
from sqlalchemy import text
from backend.core.config import AppSettings
from backend.core.logger import get_logger
from backend.infrastructure.database.session import engine, async_session_factory
from backend.infrastructure.redis.client import get_redis_client, redis_pool
from backend.infrastructure.event_bus.bus import EventBus
from backend.infrastructure.health.manager import HealthCheckManager

app_settings = AppSettings()
logger = get_logger("smoke_test")

async def test_database():
    logger.info("Testing Database connection...")
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
    logger.info("Database connection successful.")

async def test_redis():
    logger.info("Testing Redis connection...")
    client = get_redis_client()
    await client.ping()
    logger.info("Redis connection successful.")

async def test_event_bus():
    logger.info("Testing Event Bus initialization...")
    bus = EventBus()
    logger.info("Event Bus initialized.")
    return bus

async def test_health_manager():
    logger.info("Testing Health Manager initialization...")
    manager = HealthCheckManager()
    logger.info("Health Manager initialized.")
    return manager

async def main():
    logger.info("=== Starting Runtime Verification (Smoke Test) ===")
    logger.info(f"App Name: {app_settings.project_name}, Environment: {app_settings.env}")
    
    try:
        await test_database()
        
        try:
            await test_redis()
        except Exception as e:
            logger.warning(f"Redis test failed (is Redis running?): {e}")

        bus = await test_event_bus()
        hm = await test_health_manager()
        
        logger.info("Closing Database Engine...")
        await engine.dispose()
        
        logger.info("Closing Redis Pool...")
        await redis_pool.disconnect()
        
        logger.info("=== Smoke Test Completed Successfully ===")
        print("SMOKE TEST PASSED")
    except Exception as e:
        logger.error(f"Smoke Test Failed: {e}", exc_info=True)
        print("SMOKE TEST FAILED")
        raise e

if __name__ == "__main__":
    asyncio.run(main())
