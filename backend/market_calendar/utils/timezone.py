"""
Timezone and Date Utilities
"""
from datetime import datetime, date, timezone as py_timezone
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from backend.market_calendar.exceptions import InvalidTimezoneException
from backend.core.logger import get_logger

logger = get_logger(__name__)

class TimezoneUtils:
    
    @staticmethod
    def get_zoneinfo(tz_string: str) -> ZoneInfo:
        """Safely retrieves a ZoneInfo object."""
        try:
            return ZoneInfo(tz_string)
        except Exception as e:
            logger.error(f"Invalid timezone requested: {tz_string}")
            raise InvalidTimezoneException(tz_string) from e

    @staticmethod
    def utc_now() -> datetime:
        """Returns the current UTC time as an aware datetime object."""
        return datetime.now(py_timezone.utc)

    @staticmethod
    def to_exchange_local(utc_dt: datetime, exchange_tz: str) -> datetime:
        """Converts a UTC datetime to the exchange's local time."""
        if not utc_dt.tzinfo:
            utc_dt = utc_dt.replace(tzinfo=py_timezone.utc)
        return utc_dt.astimezone(TimezoneUtils.get_zoneinfo(exchange_tz))

    @staticmethod
    def to_utc(local_dt: datetime, exchange_tz: str) -> datetime:
        """Converts an exchange's local datetime to UTC."""
        if not local_dt.tzinfo:
            local_dt = local_dt.replace(tzinfo=TimezoneUtils.get_zoneinfo(exchange_tz))
        return local_dt.astimezone(py_timezone.utc)

    @staticmethod
    def get_local_date(utc_dt: datetime, exchange_tz: str) -> date:
        """Gets the local calendar date at the exchange for a given UTC timestamp."""
        return TimezoneUtils.to_exchange_local(utc_dt, exchange_tz).date()
