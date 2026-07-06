"""
Data Normalizer
"""
from typing import Any
from datetime import datetime
import dateutil.parser # type: ignore
from pydantic import ValidationError

from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.candle import Candle
from backend.historical_data.exceptions import NormalizationException

class DataNormalizer:
    """
    Transforms RawCandles into canonical Candles.
    """
    
    @staticmethod
    def _parse_timestamp(raw_timestamp: Any) -> datetime:
        if isinstance(raw_timestamp, datetime):
            if raw_timestamp.tzinfo is None:
                # Assuming UTC if naive, as per standard platform architecture
                import pytz # type: ignore
                return raw_timestamp.replace(tzinfo=pytz.UTC)
            return raw_timestamp
            
        if isinstance(raw_timestamp, (int, float)):
            # Assume milliseconds if length is long, else seconds
            if raw_timestamp > 1e11: 
                return datetime.fromtimestamp(raw_timestamp / 1000.0)
            return datetime.fromtimestamp(raw_timestamp)
            
        if isinstance(raw_timestamp, str):
            try:
                dt = dateutil.parser.isoparse(raw_timestamp)
                if dt.tzinfo is None:
                    import pytz
                    return dt.replace(tzinfo=pytz.UTC)
                return dt
            except ValueError:
                raise ValueError(f"Could not parse ISO timestamp string: {raw_timestamp}")
                
        raise ValueError(f"Unsupported timestamp format: {type(raw_timestamp)}")
        
    @staticmethod
    def _parse_float(val: Any) -> float:
        try:
            return float(val)
        except (ValueError, TypeError):
            raise ValueError(f"Could not convert to float: {val}")

    @classmethod
    def normalize(cls, raw: RawCandle) -> Candle:
        """
        Validates and converts a RawCandle to a normalized Candle.
        Raises NormalizationException if it cannot be converted.
        """
        try:
            dt = cls._parse_timestamp(raw.raw_timestamp)
            open_px = cls._parse_float(raw.raw_open)
            high_px = cls._parse_float(raw.raw_high)
            low_px = cls._parse_float(raw.raw_low)
            close_px = cls._parse_float(raw.raw_close)
            vol = cls._parse_float(raw.raw_volume)
            
            return Candle(
                symbol=raw.symbol,
                timeframe=raw.timeframe,
                timestamp=dt,
                open=open_px,
                high=high_px,
                low=low_px,
                close=close_px,
                volume=vol,
                is_completed=True
            )
        except ValidationError as ve:
            # Re-raise Pydantic mathematical validation errors (like low > high)
            raise NormalizationException(raw.symbol.symbol, str(ve))
        except ValueError as ve:
            # Parsing error
            raise NormalizationException(raw.symbol.symbol, str(ve))
        except Exception as e:
            # Catch-all
            raise NormalizationException(raw.symbol.symbol, str(e))
