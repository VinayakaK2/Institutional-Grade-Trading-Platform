import hashlib
import json
from backend.trade_validation_engine.trade_decision.models.models import DecisionContext

class BusinessFingerprintBuilder:
    """
    Pure component to deterministically generate a fingerprint from purely business-impacting fields.
    Reusable by future systems like Backtesting or Analytics.
    """
    
    @staticmethod
    def build(context: DecisionContext, decision_algorithm_version: str) -> str:
        # Determine business inputs to construct deterministic identity and fingerprint
        config_hash = hashlib.sha256(context.configuration.model_dump_json().encode('utf-8')).hexdigest()
        
        fingerprint_payload = {
            "symbol": context.symbol,
            "timeframe": context.timeframe,
            "dataset_version": context.dataset_version,
            "validation_report_version": context.validation_report_version,
            "config_hash": config_hash,
            "decision_algorithm_version": decision_algorithm_version
        }
        
        # Excludes timestamps, metadata, and UUIDs.
        return hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True).encode('utf-8')).hexdigest()
