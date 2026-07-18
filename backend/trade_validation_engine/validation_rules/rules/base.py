import abc
from backend.trade_validation_engine.signal_aggregation.models.models import AggregatedTradeEvidence
from backend.trade_validation_engine.validation_rules.models.models import ValidationContext, RuleValidationResult

class IValidationRule(abc.ABC):
    """
    Contract for a deterministic business rule in the Validation Rules Engine.
    Rules consume evidence and produce structured validation results.
    They do NOT generate new market analysis.
    """

    @property
    @abc.abstractmethod
    def rule_id(self) -> str:
        """The unique identifier for the rule."""
        pass

    @property
    @abc.abstractmethod
    def rule_version(self) -> str:
        """The version of this rule."""
        pass

    @property
    @abc.abstractmethod
    def priority(self) -> int:
        """The execution priority. Lower numbers execute earlier."""
        pass

    @abc.abstractmethod
    async def validate(
        self, 
        context: ValidationContext, 
        aggregated_evidence: AggregatedTradeEvidence
    ) -> RuleValidationResult:
        """
        Executes the deterministic validation logic against the provided evidence.
        """
        pass
