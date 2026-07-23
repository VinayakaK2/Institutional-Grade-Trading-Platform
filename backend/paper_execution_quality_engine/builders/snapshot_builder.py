import json
import hashlib
import math
from datetime import datetime, timezone
from backend.paper_execution_quality_engine.models.contexts import PaperExecutionQualityExecutionContext, PaperExecutionQualityPipelineContext
from backend.paper_execution_quality_engine.models.snapshot import PaperExecutionQualitySnapshot
from backend.paper_execution_quality_engine.models.execution_quality import ExecutionQualityReport
from backend.paper_execution_quality_engine.utils.pipeline_version import PIPELINE_VERSION
from backend.paper_execution_quality_engine.utils.snapshot_version import SnapshotVersionProvider
from backend.paper_execution_quality_engine.exceptions.exceptions import PaperExecutionQualityCalculationError

class PaperExecutionQualitySnapshotBuilder:
    """
    Responsible for validating stage invariants and building the immutable PaperExecutionQualitySnapshot.
    """
    def _validate_invariants(self, pipeline_context: PaperExecutionQualityPipelineContext) -> None:
        report = pipeline_context.execution_quality_report
        if not report:
            raise PaperExecutionQualityCalculationError("Cannot build snapshot without an ExecutionQualityReport.")

        # Slippage values internally consistent
        if math.isnan(report.slippage.slippage_amount) or math.isinf(report.slippage.slippage_amount):
            raise PaperExecutionQualityCalculationError("Slippage amount must be finite.")
            
        # Spread values internally consistent
        if report.spread_cost.bid_price > report.spread_cost.ask_price and report.spread_cost.ask_price != 0.0:
            raise PaperExecutionQualityCalculationError("Bid price cannot be greater than ask price.")
            
        # Liquidity utilization bounds
        if report.liquidity_metrics.liquidity_utilization < 0.0:
            raise PaperExecutionQualityCalculationError("Liquidity utilization cannot be negative.")
            
        # Market impact finite
        if math.isnan(report.market_impact.market_impact) or math.isinf(report.market_impact.market_impact):
            raise PaperExecutionQualityCalculationError("Market impact must be finite.")

    def build(self, execution_context: PaperExecutionQualityExecutionContext, pipeline_context: PaperExecutionQualityPipelineContext) -> PaperExecutionQualitySnapshot:
        self._validate_invariants(pipeline_context)
        
        from typing import cast
        report = cast(ExecutionQualityReport, pipeline_context.execution_quality_report)
        
        # Exclude runtime, diagnostics, telemetry, random IDs
        business_components = {
            "dataset_version": execution_context.dataset_version,
            "parent_fill_snapshot_version": execution_context.parent_snapshot_references.parent_fill_snapshot_version,
            "configuration_hash": execution_context.configuration_hash,
            "execution_quality_model_version": execution_context.execution_quality_model_version,
            "pipeline_version": PIPELINE_VERSION,
            "report": report.model_dump()
        }
        
        business_encoded = json.dumps(business_components, sort_keys=True).encode('utf-8')
        business_fingerprint = hashlib.sha256(business_encoded).hexdigest()
        
        snapshot_hash = business_fingerprint  # In this isolated context, the business fingerprint forms the core identity
        
        created_at = datetime.now(timezone.utc)
        
        snapshot_version = SnapshotVersionProvider.generate()
        
        return PaperExecutionQualitySnapshot(
            snapshot_id=snapshot_version,
            snapshot_version=snapshot_version,
            schema_version=PIPELINE_VERSION,
            dataset_version=execution_context.dataset_version,
            parent_fill_snapshot_version=execution_context.parent_snapshot_references.parent_fill_snapshot_version,
            execution_quality_report=report,
            business_fingerprint=business_fingerprint,
            snapshot_hash=snapshot_hash,
            created_at=created_at,
            metadata=execution_context.metadata
        )
