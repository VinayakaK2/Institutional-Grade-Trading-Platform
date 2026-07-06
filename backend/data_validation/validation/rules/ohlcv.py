from typing import List
from backend.historical_data.models.raw import RawCandle
from backend.data_validation.contracts.rule import ValidationRule, ValidationContext
from backend.data_validation.models.report import ValidationResult

class OhlcvRule(ValidationRule):
    """
    Validates candle consistency mathematically.
    High >= Open, High >= Low, High >= Close.
    Low <= Open, Low <= High, Low <= Close.
    Volume >= 0.
    """
    async def validate(self, context: ValidationContext, records: List[RawCandle]) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        
        for record in records:
            # Skip evaluation if not numeric (handled by StructuralRule)
            try:
                px_open = float(record.raw_open)
                px_high = float(record.raw_high)
                px_low = float(record.raw_low)
                px_close = float(record.raw_close)
                px_vol = float(record.raw_volume)
            except (ValueError, TypeError):
                continue
                
            if px_open < 0 or px_high < 0 or px_low < 0 or px_close < 0:
                results.append(ValidationResult(
                    rule_name="OhlcvRule.NegativePrice",
                    is_valid=False,
                    record_timestamp=str(record.raw_timestamp),
                    message=f"Prices cannot be negative. Got O:{px_open}, H:{px_high}, L:{px_low}, C:{px_close}"
                ))
                
            if px_vol < 0:
                results.append(ValidationResult(
                    rule_name="OhlcvRule.NegativeVolume",
                    is_valid=False,
                    record_timestamp=str(record.raw_timestamp),
                    message=f"Volume cannot be negative. Got {px_vol}"
                ))
                
            if px_high < px_open or px_high < px_close or px_high < px_low:
                results.append(ValidationResult(
                    rule_name="OhlcvRule.InvalidHigh",
                    is_valid=False,
                    record_timestamp=str(record.raw_timestamp),
                    message=f"High ({px_high}) must be >= Open, Close, and Low"
                ))
                
            if px_low > px_open or px_low > px_close or px_low > px_high:
                results.append(ValidationResult(
                    rule_name="OhlcvRule.InvalidLow",
                    is_valid=False,
                    record_timestamp=str(record.raw_timestamp),
                    message=f"Low ({px_low}) must be <= Open, Close, and High"
                ))
                
        return results
