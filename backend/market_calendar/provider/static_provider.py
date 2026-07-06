"""
Static Memory Calendar Provider
Provides hardcoded, offline-capable market calendar data. Ideal for testing and fallback.
"""
from datetime import date, time
from backend.market_calendar.provider.interface import BaseCalendarProvider
from backend.market_calendar.models.session import DailySchedule, SessionSchedule, SessionType
from backend.market_calendar.exceptions import MissingCalendarDataException

class StaticCalendarProvider(BaseCalendarProvider):
    
    @property
    def name(self) -> str:
        return "static_calendar"
        
    @property
    def is_healthy(self) -> bool:
        return True # Always healthy because it's memory-based
        
    def get_exchange_timezone(self, exchange_code: str) -> str:
        # Hardcoded timezones for testing
        timezones = {
            "NSE": "Asia/Kolkata",
            "BSE": "Asia/Kolkata",
            "NASDAQ": "America/New_York",
            "NYSE": "America/New_York"
        }
        if exchange_code not in timezones:
            raise MissingCalendarDataException(exchange_code, "N/A", f"Unknown exchange timezone: {exchange_code}")
        return timezones[exchange_code]
        
    async def get_daily_schedule(self, exchange_code: str, target_date: date) -> DailySchedule:
        # Basic Weekend Check
        is_weekend = target_date.weekday() >= 5 # 5=Sat, 6=Sun
        
        # Hardcoded Holidays for testing (e.g., 2025-01-01)
        is_holiday = (target_date.month == 1 and target_date.day == 1)
        
        if is_weekend or is_holiday:
            return DailySchedule(
                exchange_code=exchange_code,
                date_str=target_date.isoformat(),
                is_trading_day=False,
                sessions=[
                    SessionSchedule(
                        session_type=SessionType.CLOSED,
                        start_local_time=time(0, 0),
                        end_local_time=time(23, 59, 59)
                    )
                ]
            )
            
        # Normal Trading Day
        sessions = []
        if exchange_code in ["NSE", "BSE"]:
            sessions = [
                SessionSchedule(session_type=SessionType.PRE_MARKET, start_local_time=time(9, 0), end_local_time=time(9, 15)),
                SessionSchedule(session_type=SessionType.NORMAL, start_local_time=time(9, 15), end_local_time=time(15, 30)),
                SessionSchedule(session_type=SessionType.POST_MARKET, start_local_time=time(15, 40), end_local_time=time(16, 0))
            ]
        elif exchange_code in ["NASDAQ", "NYSE"]:
            sessions = [
                SessionSchedule(session_type=SessionType.PRE_MARKET, start_local_time=time(4, 0), end_local_time=time(9, 30)),
                SessionSchedule(session_type=SessionType.NORMAL, start_local_time=time(9, 30), end_local_time=time(16, 0)),
                SessionSchedule(session_type=SessionType.POST_MARKET, start_local_time=time(16, 0), end_local_time=time(20, 0))
            ]
        else:
            raise MissingCalendarDataException(exchange_code, target_date.isoformat(), "Unsupported exchange.")
            
        return DailySchedule(
            exchange_code=exchange_code,
            date_str=target_date.isoformat(),
            is_trading_day=True,
            sessions=sessions
        )
