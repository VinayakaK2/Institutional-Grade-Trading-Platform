import hashlib
import json
from backend.risk_optimization_engine.models.request import OptimizationRequest

class FingerprintGenerator:
    """
    Deterministically generates hashes for business fingerprints.
    """
    
    @staticmethod
    def generate_cache_key(request: OptimizationRequest) -> str:
        """
        Generates the cache key: BusinessFingerprint hash + Pipeline Version.
        """
        fingerprint = request.fingerprint
        key_data = {
            "fingerprint_hash": fingerprint.fingerprint_hash,
            "pipeline_version": request.pipeline_version
        }
        return hashlib.sha256(json.dumps(key_data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        
    @staticmethod
    def generate_fingerprint_hash(
        dataset_version: str,
        algorithm_versions: dict,
        rule_versions: dict,
        strategy_version: str,
        parent_snapshot_id: str,
        risk_percentage: float,
        position_sizing_config: dict,
        portfolio_config: dict,
        decision_config: dict,
        exchange_config: dict = None
    ) -> str:
        data = {
            "dataset_version": dataset_version,
            "algorithm_versions": algorithm_versions,
            "rule_versions": rule_versions,
            "strategy_version": strategy_version,
            "parent_snapshot_id": parent_snapshot_id,
            "risk_percentage": risk_percentage,
            "position_sizing_config": position_sizing_config,
            "portfolio_config": portfolio_config,
            "decision_config": decision_config,
            "exchange_config": exchange_config or {}
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
