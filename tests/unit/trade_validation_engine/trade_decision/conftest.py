import pytest
from backend.trade_validation_engine.trade_decision.config.config import TradeDecisionConfig
from backend.trade_validation_engine.trade_decision.models.models import (
    DecisionContext, DecisionState, RejectionReason, DecisionEvidence, StageExecutionResult
)
from backend.trade_validation_engine.trade_decision.pipeline.pipeline import IDecisionStage
from backend.trade_validation_engine.validation_rules.models.models import ValidationReport, ValidationReportSummary, ValidationStatus

@pytest.fixture
def valid_context():
    return DecisionContext(
        symbol="BTC/USD",
        timeframe="1H",
        dataset_version=1,
        validation_report_version="rep_1",
        configuration=TradeDecisionConfig(fail_fast=True),
        metadata={}
    )

@pytest.fixture
def mock_validation_report():
    return ValidationReport(
        validation_id="rep_1",
        symbol="BTC/USD",
        timeframe="1H",
        dataset_version=1,
        configuration_hash="dummy",
        validation_pipeline_version="1.0",
        status=ValidationStatus.PASS,
        rule_results=[],
        summary=ValidationReportSummary(
            total_rules_executed=0, passed_rules=0, failed_rules=0, skipped_rules=0, total_duration_ms=0
        )
    )

class MockValidStage(IDecisionStage):
    @property
    def stage_id(self): return "mock_valid"
    
    async def execute(self, context, report):
        return StageExecutionResult(
            stage_id=self.stage_id,
            state=DecisionState.VALID,
            execution_duration_ms=10,
            evidence=DecisionEvidence(evidence_type="Mock", verified_properties={"ok": True})
        )

class MockInvalidStage(IDecisionStage):
    @property
    def stage_id(self): return "mock_invalid"
    
    async def execute(self, context, report):
        return StageExecutionResult(
            stage_id=self.stage_id,
            state=DecisionState.INVALID,
            rejection_reasons=[RejectionReason.VALIDATION_FAILED],
            execution_duration_ms=10
        )
