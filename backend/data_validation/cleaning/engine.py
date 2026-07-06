from typing import List, Set
import time
from backend.historical_data.models.raw import RawCandle
from backend.data_validation.contracts.rule import CleaningRule
from backend.data_validation.models.cleaning import CleaningResult
from backend.data_validation.models.report import ValidationReport

class CleaningEngine:
    """
    Applies configurable cleaning rules.
    Partitions valid vs rejected records based on ValidationReport findings.
    """
    def __init__(self, rules: List[CleaningRule]):
        self.rules = rules

    async def run(self, records: List[RawCandle], validation_report: ValidationReport) -> CleaningResult:
        start_time = time.time()
        result = CleaningResult()
        
        # 1. Identify inherently invalid records from the validation report
        # We collect the timestamps of records that failed hard validation rules (Structural, OHLCV)
        invalid_timestamps: Set[str] = set()
        
        for error in validation_report.structural_findings.errors:
            if error.record_timestamp:
                invalid_timestamps.add(error.record_timestamp)
                
        for error in validation_report.ohlcv_findings.errors:
            if error.record_timestamp:
                invalid_timestamps.add(error.record_timestamp)
                
        # 2. Partition data
        valid_records = []
        for r in records:
            if str(r.raw_timestamp) in invalid_timestamps:
                result.rejected_records.append(r)
            else:
                valid_records.append(r)
                result.valid_records.append(r)
                
        # 3. Apply Cleaning Rules on valid data
        cleaned_records = valid_records
        for rule in self.rules:
            # We track duplicates or other removals by length difference
            pre_len = len(cleaned_records)
            cleaned_records = await rule.clean(cleaned_records)
            post_len = len(cleaned_records)
            
            if post_len < pre_len:
                result.cleaning_actions.append(f"{rule.__class__.__name__} removed {pre_len - post_len} records")
                
        result.cleaned_records = cleaned_records
        
        # Add to rejected any that the cleaning rules removed
        # (e.g. duplicates). Use object id to differentiate duplicates with same timestamp.
        cleaned_ids = {id(r) for r in cleaned_records}
        for r in valid_records:
            if id(r) not in cleaned_ids:
                result.rejected_records.append(r)
                
        result.statistics['total_input'] = len(records)
        result.statistics['total_valid_pre_clean'] = len(valid_records)
        result.statistics['total_cleaned_output'] = len(cleaned_records)
        result.statistics['total_rejected'] = len(result.rejected_records)
        
        result.duration_seconds = time.time() - start_time
        return result
