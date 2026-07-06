import time
import hashlib
from typing import List, Tuple, Optional

from backend.corporate_actions.models.action import CorporateAction, ActionStatus
from backend.corporate_actions.models.adjustment import AdjustmentMode
from backend.corporate_actions.models.versioning import DatasetVersion, AuditLog
from backend.corporate_actions.models.report import PipelineReport
from backend.corporate_actions.contracts.storage import CorporateActionRepository, DatasetVersionRepository, AuditLogRepository
from backend.corporate_actions.validation.engine import ValidationEngine
from backend.corporate_actions.adjustment.engine import AdjustmentEngine
from backend.market_data.models.candle import Candle
from backend.market_data.models.symbol import SymbolReference

class CorporateActionsPipeline:
    """Orchestrates ingestion, validation, and storage of raw corporate actions."""
    
    def __init__(
        self,
        action_repo: CorporateActionRepository,
        audit_repo: AuditLogRepository,
        validation_engine: ValidationEngine
    ):
        self.action_repo = action_repo
        self.audit_repo = audit_repo
        self.validation_engine = validation_engine
        
    def process_actions(self, raw_actions: List[CorporateAction]) -> PipelineReport:
        start_time = time.time()
        existing_actions = self.action_repo.get_all()
        
        valid_actions, errors = self.validation_engine.validate(raw_actions, existing_actions)
        
        affected_symbols = set()
        
        for action in valid_actions:
            self.action_repo.save(action)
            affected_symbols.add(action.symbol.full_name)
            
            # Audit log
            log = AuditLog(
                action_id=action.id,
                event_type="VALIDATED_AND_STORED",
                details=f"Stored {action.action_type} for {action.symbol.full_name}"
            )
            self.audit_repo.save(log)
            
        for invalid_action, reason in errors:
            invalid_action.status = ActionStatus.REJECTED # User specified PENDING -> VALIDATED -> APPLIED (or REJECTED)
            # We don't save rejected actions to the main repository, but we log them
            log = AuditLog(
                action_id=invalid_action.id,
                event_type="REJECTED",
                details=reason
            )
            self.audit_repo.save(log)
            
        duration = time.time() - start_time
        
        error_dicts = [{"action_id": a.id, "reason": r} for a, r in errors]
        
        return PipelineReport(
            total_actions=len(raw_actions),
            applied_actions=len(valid_actions), # In this context, "applied to repo"
            rejected_actions=len(errors),
            symbols_affected=len(affected_symbols),
            processing_duration_seconds=duration,
            validation_errors=error_dicts
        )

class DatasetAdjustmentPipeline:
    """Orchestrates applying corporate actions to a canonical dataset and generating a new version."""
    
    def __init__(
        self,
        action_repo: CorporateActionRepository,
        version_repo: DatasetVersionRepository,
        audit_repo: AuditLogRepository,
        adjustment_engine: AdjustmentEngine
    ):
        self.action_repo = action_repo
        self.version_repo = version_repo
        self.audit_repo = audit_repo
        self.adjustment_engine = adjustment_engine
        
    def _generate_dataset_hash(self, dataset: List[Candle]) -> str:
        # A simple hash based on candle timestamps and closes
        # In a real system, this could just be a UUID or a Merkle root.
        hasher = hashlib.sha256()
        for c in dataset:
            data = f"{c.timestamp.isoformat()}:{c.close}"
            hasher.update(data.encode('utf-8'))
        return hasher.hexdigest()
        
    def adjust_dataset(self, symbol: SymbolReference, dataset: List[Candle], mode: AdjustmentMode = AdjustmentMode.FULLY_ADJUSTED) -> Tuple[List[Candle], Optional[DatasetVersion]]:
        if not dataset:
            return dataset, None
            
        actions = self.action_repo.get_by_symbol(symbol)
        valid_actions = [a for a in actions if a.status in {ActionStatus.VALIDATED, ActionStatus.APPLIED}]
        
        original_hash = self._generate_dataset_hash(dataset)
        
        adjusted_dataset = self.adjustment_engine.adjust(dataset, valid_actions, mode)
        
        adjusted_hash = self._generate_dataset_hash(adjusted_dataset)
        
        applied_action_ids = [a.id for a in valid_actions]
        
        version = DatasetVersion(
            original_version=original_hash,
            adjusted_version=adjusted_hash,
            applied_action_ids=applied_action_ids,
            adjustment_mode=mode
        )
        
        self.version_repo.save(version)
        
        for action in valid_actions:
            if action.status != ActionStatus.APPLIED:
                action.status = ActionStatus.APPLIED
                self.action_repo.save(action)
                
            log = AuditLog(
                action_id=action.id,
                event_type="APPLIED",
                details=f"Applied to dataset {original_hash} -> {adjusted_hash} via mode {mode}"
            )
            self.audit_repo.save(log)
            
        return adjusted_dataset, version
