"""
Market Time Service
The application-facing API for resolving market states, dates, and times.
"""
from datetime import datetime, date, timedelta
from typing import Optional, Tuple
from backend.market_calendar.provider.manager import CalendarProviderManager
from backend.market_calendar.models.session import SessionType, SessionSchedule
from backend.market_calendar.utils.timezone import TimezoneUtils
from backend.infrastructure.cache.manager import CacheManager
from backend.core.logger import get_logger

logger = get_logger(__name__)

class MarketTimeService:
    def __init__(self, provider_manager: CalendarProviderManager, cache_manager: CacheManager):
        self._manager = provider_manager
        self._cache = cache_manager

    async def get_exchange_timezone(self, exchange_code: str) -> str:
        """Retrieves the timezone for the exchange."""
        cache_key = f"calendar:tz:{exchange_code}"
        cached = await self._cache.get("market_calendar", "timezone", cache_key)
        if cached:
            return cached

        async def fetch_tz(provider):
            return provider.get_exchange_timezone(exchange_code)
            
        tz = await self._manager.execute(fetch_tz, "get_exchange_timezone")
        await self._cache.set("market_calendar", "timezone", cache_key, tz, ttl=86400 * 30) # 30 days cache
        return tz

    async def is_market_open(self, exchange_code: str, utc_dt: Optional[datetime] = None) -> bool:
        """Checks if the market is currently in the NORMAL trading session."""
        target_utc = utc_dt or TimezoneUtils.utc_now()
        session, _ = await self.get_current_session(exchange_code, target_utc)
        return session == SessionType.NORMAL

    async def is_trading_day(self, exchange_code: str, target_date: date) -> bool:
        """Checks if the given date is a trading day (not a weekend/holiday)."""
        async def fetch_schedule(provider):
            return await provider.get_daily_schedule(exchange_code, target_date)
            
        schedule = await self._manager.execute(fetch_schedule, "is_trading_day")
        return schedule.is_trading_day

    async def get_current_session(self, exchange_code: str, utc_dt: Optional[datetime] = None) -> Tuple[SessionType, Optional[SessionSchedule]]:
        """Resolves the current session type based on the UTC timestamp."""
        target_utc = utc_dt or TimezoneUtils.utc_now()
        exchange_tz = await self.get_exchange_timezone(exchange_code)
        
        local_dt = TimezoneUtils.to_exchange_local(target_utc, exchange_tz)
        local_date = local_dt.date()
        local_time = local_dt.time()
        
        async def fetch_schedule(provider):
            return await provider.get_daily_schedule(exchange_code, local_date)
            
        schedule = await self._manager.execute(fetch_schedule, "get_current_session")
        
        if not schedule.is_trading_day:
            return SessionType.CLOSED, None
            
        for session in schedule.sessions:
            if session.start_local_time <= local_time <= session.end_local_time:
                return session.session_type, session
                
        return SessionType.CLOSED, None

    async def get_next_trading_day(self, exchange_code: str, from_date: date) -> date:
        """Iterates forward to find the next valid trading day."""
        current_date = from_date + timedelta(days=1)
        # Prevent infinite loops (e.g. invalid exchange)
        for _ in range(30):
            if await self.is_trading_day(exchange_code, current_date):
                return current_date
            current_date += timedelta(days=1)
            
        raise RuntimeError("Could not find a valid trading day within 30 days forward.")
