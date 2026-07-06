from typing import List
from backend.historical_data.models.raw import RawCandle
from backend.data_validation.contracts.rule import ValidationRule, ValidationContext
from backend.data_validation.models.report import ValidationResult
from datetime import datetime
import dateutil.parser

class StructuralRule(ValidationRule):
    """
    Validates basic candle integrity.
    Checks: nulls, data types, required fields, basic timestamp validity.
    """
    async def validate(self, context: ValidationContext, records: List[RawCandle]) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        
        for record in records:
            # 1. Null Detection
            null_fields = []
            for field in ['raw_timestamp', 'raw_open', 'raw_high', 'raw_low', 'raw_close', 'raw_volume']:
                if getattr(record, field) is None:
                    null_fields.append(field)
                    
            if null_fields:
                results.append(
                    ValidationResult(
                        rule_name="StructuralRule.NullDetection",
                        is_valid=False,
                        record_timestamp=str(record.raw_timestamp),
                        message=f"Fields cannot be null: {', '.join(null_fields)}"
                    )
                )
                
            # 2. Numeric Type Validation
            for field in ['raw_open', 'raw_high', 'raw_low', 'raw_close', 'raw_volume']:
                val = getattr(record, field)
                if val is not None:
                    try:
                        float(val)
                    except (ValueError, TypeError):
                        results.append(
                            ValidationResult(
                                rule_name="StructuralRule.TypeValidation",
                                is_valid=False,
                                record_timestamp=str(record.raw_timestamp),
                                message=f"Field {field} must be numeric. Got {type(val)}: {val}"
                            )
                        )
            
            # 3. Timestamp Validation
            if record.raw_timestamp is not None:
                try:
                    if isinstance(record.raw_timestamp, (int, float)):
                        # Assume unix timestamp
                        pass # Valid
                    elif isinstance(record.raw_timestamp, str):
                        dateutil.parser.parse(record.raw_timestamp)
                    elif isinstance(record.raw_timestamp, datetime):
                        pass
                    else:
                        raise ValueError()
                except (ValueError, TypeError, OverflowError):
                    results.append(
                        ValidationResult(
                            rule_name="StructuralRule.TimestampValidation",
                            is_valid=False,
                            record_timestamp=str(record.raw_timestamp),
                            message=f"Invalid timestamp format: {record.raw_timestamp}"
                        )
                    )
                    
        return results
