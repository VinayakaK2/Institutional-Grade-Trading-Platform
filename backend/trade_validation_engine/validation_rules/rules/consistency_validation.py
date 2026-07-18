from backend.trade_validation_engine.signal_aggregation.models.models import AggregatedTradeEvidence
from backend.trade_validation_engine.validation_rules.models.models import ValidationContext, RuleValidationResult, ValidationEvidence
from backend.trade_validation_engine.validation_rules.rules.base import IValidationRule

class DatasetConsistencyRule(IValidationRule):
    @property
    def rule_id(self) -> str:
        return "dataset_consistency_rule"

    @property
    def rule_version(self) -> str:
        return "1.0.0"

    @property
    def priority(self) -> int:
        return 10

    async def validate(self, context: ValidationContext, aggregated_evidence: AggregatedTradeEvidence) -> RuleValidationResult:
        if context.dataset_version != aggregated_evidence.dataset_version:
            return RuleValidationResult(
                rule_id=self.rule_id,
                rule_version=self.rule_version,
                status="FAIL",
                reason="Dataset version mismatch between context and evidence.",
                validation_evidence=ValidationEvidence(
                    verified_properties={
                        "context_dataset_version": context.dataset_version,
                        "evidence_dataset_version": aggregated_evidence.dataset_version
                    },
                    expected_values={"evidence_dataset_version": context.dataset_version}
                )
            )
        
        return RuleValidationResult(
            rule_id=self.rule_id,
            rule_version=self.rule_version,
            status="PASS",
            validation_evidence=ValidationEvidence(
                verified_properties={
                    "context_dataset_version": context.dataset_version,
                    "evidence_dataset_version": aggregated_evidence.dataset_version
                },
                expected_values={"evidence_dataset_version": context.dataset_version}
            )
        )


class SnapshotLineageRule(IValidationRule):
    @property
    def rule_id(self) -> str:
        return "snapshot_lineage_rule"

    @property
    def rule_version(self) -> str:
        return "1.0.0"

    @property
    def priority(self) -> int:
        return 11

    async def validate(self, context: ValidationContext, aggregated_evidence: AggregatedTradeEvidence) -> RuleValidationResult:
        if context.symbol != aggregated_evidence.symbol or context.timeframe != aggregated_evidence.timeframe:
            return RuleValidationResult(
                rule_id=self.rule_id,
                rule_version=self.rule_version,
                status="FAIL",
                reason="Symbol or timeframe lineage mismatch.",
                validation_evidence=ValidationEvidence(
                    verified_properties={
                        "context_symbol": context.symbol,
                        "evidence_symbol": aggregated_evidence.symbol,
                        "context_timeframe": context.timeframe,
                        "evidence_timeframe": aggregated_evidence.timeframe
                    },
                    expected_values={
                        "evidence_symbol": context.symbol,
                        "evidence_timeframe": context.timeframe
                    }
                )
            )

        return RuleValidationResult(
            rule_id=self.rule_id,
            rule_version=self.rule_version,
            status="PASS",
            validation_evidence=ValidationEvidence(
                verified_properties={
                    "symbol_match": True,
                    "timeframe_match": True
                },
                expected_values={"symbol_match": True, "timeframe_match": True}
            )
        )
