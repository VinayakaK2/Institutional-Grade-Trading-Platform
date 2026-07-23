import logging
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext
from backend.paper_execution_quality_engine.models.snapshot import PaperExecutionQualitySnapshot
from backend.paper_execution_quality_engine.utils.pipeline_version import PIPELINE_VERSION

class PaperExecutionQualityLogger:
    def __init__(self):
        self._logger = logging.getLogger("PaperExecutionQualityEngine")

    def log_execution_start(self, context: PaperExecutionQualityExecutionContext) -> None:
        self._logger.info(f"Starting execution quality pipeline {PIPELINE_VERSION} for symbol {context.symbol} against fill {context.parent_snapshot_references.parent_fill_snapshot_version}")

    def log_snapshot_created(self, snapshot: PaperExecutionQualitySnapshot) -> None:
        self._logger.info(f"Snapshot generated: {snapshot.snapshot_version} (Business Fingerprint: {snapshot.business_fingerprint})")
        
    def log_validation_warning(self, warning: str) -> None:
        self._logger.warning(f"Validation warning: {warning}")

    def log_error(self, error: Exception) -> None:
        self._logger.error(f"Pipeline error: {str(error)}")
