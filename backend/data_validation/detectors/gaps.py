from typing import List, Optional
from datetime import timedelta
from backend.historical_data.models.raw import RawCandle
from backend.data_validation.contracts.rule import ValidationRule, ValidationContext
from backend.data_validation.models.report import ValidationResult
from backend.market_calendar.service.time_service import MarketTimeService
from backend.historical_data.engine.normalizer import DataNormalizer
from backend.market_data.models.timeframe import Timeframe

class GapDetector(ValidationRule):
    """
    Detects missing market data sequences based on the Market Calendar.
    Requires MarketTimeService in context.dependencies['market_time_service'].
    """
    async def validate(self, context: ValidationContext, records: List[RawCandle]) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        if not records:
            return results
            
        market_time_service: Optional[MarketTimeService] = context.dependencies.get('market_time_service')
        if not market_time_service:
            # Cannot accurately validate gaps without the market calendar
            return results
            
        exchange_code = context.symbol.exchange.code
        
        # Sort records by timestamp to ensure sequential check
        valid_records = []
        for r in records:
            try:
                dt = DataNormalizer._parse_timestamp(r.raw_timestamp)
                valid_records.append((dt, r))
            except Exception:
                continue # nosec B112
                
        valid_records.sort(key=lambda x: x[0])
        
        if len(valid_records) < 2:
            return results
            
        # Delta mapping
        timeframe_deltas = {
            Timeframe.M1: timedelta(minutes=1),
            Timeframe.M5: timedelta(minutes=5),
            Timeframe.M15: timedelta(minutes=15),
            Timeframe.M30: timedelta(minutes=30),
            Timeframe.H1: timedelta(hours=1),
            Timeframe.H4: timedelta(hours=4),
            Timeframe.D1: timedelta(days=1),
        }
        
        expected_delta = timeframe_deltas.get(context.timeframe)
        if not expected_delta:
            return results # E.g. Ticks or unsupported timeframe
            
        for i in range(1, len(valid_records)):
            prev_dt, _ = valid_records[i-1]
            curr_dt, curr_record = valid_records[i]
            
            diff = curr_dt - prev_dt
            
            # If difference is exactly the timeframe delta, no gap
            if diff <= expected_delta:
                continue
                
            # There is a gap > timeframe. 
            # We must verify if the gap occurred during OPEN market hours.
            # D1 check
            if context.timeframe == Timeframe.D1:
                # Iterate from prev_dt + 1 day to curr_dt - 1 day to see if there were trading days
                check_dt = prev_dt + expected_delta
                missing_days = 0
                while check_dt < curr_dt:
                    is_open = await market_time_service.is_trading_day(exchange_code, check_dt.date())
                    if is_open:
                        missing_days += 1
                    check_dt += expected_delta
                    
                if missing_days > 0:
                    results.append(ValidationResult(
                        rule_name="GapDetector.MissingTradingDay",
                        is_valid=False,
                        record_timestamp=str(curr_record.raw_timestamp),
                        message=f"Gap detected: Missing {missing_days} trading days between {prev_dt} and {curr_dt}"
                    ))
            else:
                # Intraday Check (Simplified for now - detect basic gaps, 
                # but an exhaustive intraday check requires walking the schedule hourly).
                # For Phase 2.5, we flag it if diff > delta AND they are on the same trading day.
                # Cross-day gaps are expected unless the next timestamp skips a trading day.
                
                if curr_dt.date() == prev_dt.date():
                    # Same day gap
                    is_open = await market_time_service.is_trading_day(exchange_code, curr_dt.date())
                    if is_open:
                        missing_bars = int(diff.total_seconds() / expected_delta.total_seconds()) - 1
                        if missing_bars > 0:
                            results.append(ValidationResult(
                                rule_name="GapDetector.MissingIntradayBar",
                                is_valid=False,
                                record_timestamp=str(curr_record.raw_timestamp),
                                message=f"Gap detected: Missing {missing_bars} intraday bars between {prev_dt} and {curr_dt}"
                            ))
                else:
                    # Cross day gap: check if any trading days were missed in between
                    check_date = prev_dt.date() + timedelta(days=1)
                    missing_days = 0
                    while check_date < curr_dt.date():
                        if await market_time_service.is_trading_day(exchange_code, check_date):
                            missing_days += 1
                        check_date += timedelta(days=1)
                        
                    if missing_days > 0:
                        results.append(ValidationResult(
                            rule_name="GapDetector.MissingTradingDay",
                            is_valid=False,
                            record_timestamp=str(curr_record.raw_timestamp),
                            message=f"Gap detected: Missing {missing_days} trading days between {prev_dt} and {curr_dt}"
                        ))

        return results
