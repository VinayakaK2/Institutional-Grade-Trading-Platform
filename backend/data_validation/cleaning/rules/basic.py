from typing import List
from backend.historical_data.models.raw import RawCandle
from backend.data_validation.contracts.rule import CleaningRule

class DuplicateRemovalRule(CleaningRule):
    """
    Removes exact duplicate records based on timestamp.
    Keeps the first occurrence.
    """
    async def clean(self, records: List[RawCandle]) -> List[RawCandle]:
        seen_timestamps = set()
        cleaned = []
        for record in records:
            if record.raw_timestamp not in seen_timestamps:
                seen_timestamps.add(record.raw_timestamp)
                cleaned.append(record)
        return cleaned

class WhitespaceCleanupRule(CleaningRule):
    """
    Strips leading/trailing whitespace from string fields.
    """
    async def clean(self, records: List[RawCandle]) -> List[RawCandle]:
        for record in records:
            if isinstance(record.raw_timestamp, str):
                record.raw_timestamp = record.raw_timestamp.strip()
            # Symbol strings are inside SymbolReference, but if there's extra string metadata:
            for key, val in record.extra_data.items():
                if isinstance(val, str):
                    record.extra_data[key] = val.strip()
        return records
