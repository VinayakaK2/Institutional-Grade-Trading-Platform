from typing import List
from datetime import datetime
import time

from backend.historical_data.models.raw import RawCandle
from backend.data_validation.contracts.rule import ValidationRule, ValidationContext
from backend.data_validation.models.report import ValidationReport, ValidationResult

class ValidationEngine:
    """
    Executes a suite of validation rules against a batch of raw records.
    Produces a structured ValidationReport.
    It NEVER modifies data.
    """
    def __init__(self, rules: List[ValidationRule]):
        self.rules = rules

    async def run(self, context: ValidationContext, records: List[RawCandle]) -> ValidationReport:
        start_time = time.time()
        
        report = ValidationReport(
            total_records_processed=len(records),
            execution_time=datetime.utcnow()
        )
        
        all_results: List[ValidationResult] = []
        for rule in self.rules:
            # Note: Rules run independently, which is good for performance
            # In a highly optimized version, these could run via asyncio.gather
            rule_results = await rule.validate(context, records)
            all_results.extend(rule_results)
            
        # Organize results into report
        invalid_record_timestamps = set()
        
        for res in all_results:
            if not res.is_valid:
                invalid_record_timestamps.add(res.record_timestamp)
                
            # Categorize
            if "Structural" in res.rule_name:
                report.structural_findings.errors.append(res)
            elif "Ohlcv" in res.rule_name:
                report.ohlcv_findings.errors.append(res)
            elif "Gap" in res.rule_name:
                report.gap_findings.errors.append(res)
            elif "Anomaly" in res.rule_name:
                report.anomaly_findings.warnings.append(res) # Anomalies are usually warnings, but we'll categorize as warnings for now.
            else:
                # Catch-all
                report.structural_findings.warnings.append(res)

        report.invalid_records_count = len(invalid_record_timestamps)
        report.valid_records_count = len(records) - report.invalid_records_count
        report.duration_seconds = time.time() - start_time
        
        return report
