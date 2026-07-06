"""
Tests for Timezone Utilities
"""
import pytest
from datetime import datetime, date
from backend.market_calendar.utils.timezone import TimezoneUtils
from backend.market_calendar.exceptions import InvalidTimezoneException
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

def test_valid_timezone_retrieval():
    tz = TimezoneUtils.get_zoneinfo("Asia/Kolkata")
    assert isinstance(tz, zoneinfo.ZoneInfo)
    
def test_invalid_timezone_raises_exception():
    with pytest.raises(InvalidTimezoneException):
        TimezoneUtils.get_zoneinfo("Mars/City")

def test_utc_to_exchange_local():
    # 2025-01-01 04:00:00 UTC -> 09:30:00 IST (Asia/Kolkata is +05:30)
    utc_dt = datetime(2025, 1, 1, 4, 0, 0)
    local_dt = TimezoneUtils.to_exchange_local(utc_dt, "Asia/Kolkata")
    
    assert local_dt.hour == 9
    assert local_dt.minute == 30
    assert local_dt.date() == date(2025, 1, 1)

def test_local_to_utc():
    # 2025-01-01 09:30:00 IST -> 04:00:00 UTC
    local_dt = datetime(2025, 1, 1, 9, 30, 0)
    utc_dt = TimezoneUtils.to_utc(local_dt, "Asia/Kolkata")
    
    assert utc_dt.hour == 4
    assert utc_dt.minute == 0
