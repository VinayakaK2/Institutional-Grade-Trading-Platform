from backend.trade_validation_engine.signal_aggregation.models.models import AggregatedTradeEvidence
from backend.trade_validation_engine.validation_rules.models.models import ValidationContext, RuleValidationResult, ValidationEvidence
from backend.trade_validation_engine.validation_rules.rules.base import IValidationRule

class TrendEvidenceRule(IValidationRule):
    @property
    def rule_id(self) -> str:
        return "trend_evidence_rule"

    @property
    def rule_version(self) -> str:
        return "1.0.0"

    @property
    def priority(self) -> int:
        return 20

    async def validate(self, context: ValidationContext, aggregated_evidence: AggregatedTradeEvidence) -> RuleValidationResult:
        if not aggregated_evidence.trend_evidence:
            return RuleValidationResult(
                rule_id=self.rule_id,
                rule_version=self.rule_version,
                status="FAIL",
                reason="Trend evidence is missing from aggregated evidence.",
                validation_evidence=ValidationEvidence(
                    verified_properties={"trend_evidence_exists": False},
                    expected_values={"trend_evidence_exists": True}
                )
            )

        trend_state = aggregated_evidence.trend_evidence.trend_state
        if not trend_state:
            return RuleValidationResult(
                rule_id=self.rule_id,
                rule_version=self.rule_version,
                status="FAIL",
                reason="Trend state is missing.",
                validation_evidence=ValidationEvidence(
                    verified_properties={"trend_state": None},
                    expected_values={"trend_state": "Valid UPTREND or DOWNTREND"}
                )
            )

        return RuleValidationResult(
            rule_id=self.rule_id,
            rule_version=self.rule_version,
            status="PASS",
            validation_evidence=ValidationEvidence(
                verified_properties={"trend_evidence_exists": True, "trend_state": trend_state},
                expected_values={"trend_evidence_exists": True}
            )
        )


class ConsolidationEvidenceRule(IValidationRule):
    @property
    def rule_id(self) -> str:
        return "consolidation_evidence_rule"

    @property
    def rule_version(self) -> str:
        return "1.0.0"

    @property
    def priority(self) -> int:
        return 21

    async def validate(self, context: ValidationContext, aggregated_evidence: AggregatedTradeEvidence) -> RuleValidationResult:
        if not aggregated_evidence.consolidation_evidence:
            return RuleValidationResult(
                rule_id=self.rule_id,
                rule_version=self.rule_version,
                status="FAIL",
                reason="Consolidation evidence is missing from aggregated evidence.",
                validation_evidence=ValidationEvidence(
                    verified_properties={"consolidation_evidence_exists": False},
                    expected_values={"consolidation_evidence_exists": True}
                )
            )

        return RuleValidationResult(
            rule_id=self.rule_id,
            rule_version=self.rule_version,
            status="PASS",
            validation_evidence=ValidationEvidence(
                verified_properties={
                    "consolidation_evidence_exists": True,
                    "consolidation_state": aggregated_evidence.consolidation_evidence.consolidation_state
                },
                expected_values={"consolidation_evidence_exists": True}
            )
        )


class LiquidityGrabEvidenceRule(IValidationRule):
    @property
    def rule_id(self) -> str:
        return "liquidity_grab_evidence_rule"

    @property
    def rule_version(self) -> str:
        return "1.0.0"

    @property
    def priority(self) -> int:
        return 22

    async def validate(self, context: ValidationContext, aggregated_evidence: AggregatedTradeEvidence) -> RuleValidationResult:
        if not aggregated_evidence.liquidity_grab_evidence:
            return RuleValidationResult(
                rule_id=self.rule_id,
                rule_version=self.rule_version,
                status="FAIL",
                reason="Liquidity Grab evidence is missing from aggregated evidence.",
                validation_evidence=ValidationEvidence(
                    verified_properties={"liquidity_grab_evidence_exists": False},
                    expected_values={"liquidity_grab_evidence_exists": True}
                )
            )

        return RuleValidationResult(
            rule_id=self.rule_id,
            rule_version=self.rule_version,
            status="PASS",
            validation_evidence=ValidationEvidence(
                verified_properties={
                    "liquidity_grab_evidence_exists": True,
                    "liquidity_grab_state": aggregated_evidence.liquidity_grab_evidence.liquidity_grab_state
                },
                expected_values={"liquidity_grab_evidence_exists": True}
            )
        )
