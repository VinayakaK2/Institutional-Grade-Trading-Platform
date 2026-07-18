import hashlib
import json
from typing import List
from backend.trade_validation_engine.trade_decision.models.models import (
    DecisionContext,
    StageExecutionResult,
    DecisionState,
    RejectionReason,
    TradeDecisionSnapshot
)
from backend.trade_validation_engine.trade_decision.config.config import TRADE_DECISION_ALGORITHM_VERSION

class TradeDecisionBuilder:
    """
    Assembles the final immutable TradeDecisionSnapshot and ensures
    deterministic decision_id generation using SHA-256 over business inputs.
    """
    
    @staticmethod
    def build(
        context: DecisionContext,
        final_state: DecisionState,
        rejection_reasons: List[RejectionReason],
        stage_results: List[StageExecutionResult]
    ) -> TradeDecisionSnapshot:
        
        # Determine business inputs to construct deterministic identity and fingerprint
        config_hash = hashlib.sha256(context.configuration.model_dump_json().encode('utf-8')).hexdigest()
        
        fingerprint_payload = {
            "symbol": context.symbol,
            "timeframe": context.timeframe,
            "dataset_version": context.dataset_version,
            "validation_report_version": context.validation_report_version,
            "config_hash": config_hash,
            "final_state": final_state.value,
            "rejection_reasons": [r.value for r in rejection_reasons]
        }
        
        business_fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True).encode('utf-8')).hexdigest()
        
        payload = (
            f"{context.validation_report_version}_"
            f"{context.dataset_version}_"
            f"{config_hash}_"
            f"{TRADE_DECISION_ALGORITHM_VERSION}"
        )
        decision_id = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        
        return TradeDecisionSnapshot(
            decision_id=decision_id,
            business_fingerprint=business_fingerprint,
            symbol=context.symbol,
            timeframe=context.timeframe,
            dataset_version=context.dataset_version,
            validation_report_version=context.validation_report_version,
            decision_state=final_state,
            rejection_reasons=rejection_reasons,
            stage_results=stage_results,
            metadata=context.metadata
        )
