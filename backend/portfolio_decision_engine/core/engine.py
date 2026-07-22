import uuid
from backend.portfolio_decision_engine.models.contexts import (
    PortfolioDecisionExecutionContext,
    PortfolioDecisionPipelineContext
)
from backend.portfolio_decision_engine.models.snapshot import PortfolioDecisionSnapshot
from backend.portfolio_decision_engine.contracts.repository import IPortfolioDecisionRepository
from backend.portfolio_decision_engine.rules.structural_rules import PortfolioDecisionStructuralRules
from backend.portfolio_decision_engine.rules.consistency_rules import PortfolioDecisionConsistencyRules
from backend.portfolio_decision_engine.pipeline.decision_aggregation import DecisionAggregationStage
from backend.portfolio_decision_engine.pipeline.decision_rules import DecisionRulesStage
from backend.portfolio_decision_engine.builders.snapshot_builder import PortfolioDecisionSnapshotBuilder

class PortfolioDecisionEngine:
    """
    Orchestrates the evaluation of a candidate position against portfolio constraints
    and upstream risk decisions. Produces an immutable PortfolioDecisionSnapshot.
    """
    def __init__(self, repository: IPortfolioDecisionRepository):
        self._repository = repository
        self._structural_rules = PortfolioDecisionStructuralRules()
        self._consistency_rules = PortfolioDecisionConsistencyRules()
        self._pipeline_stages = [
            DecisionAggregationStage(),
            DecisionRulesStage()
        ]
        self._builder = PortfolioDecisionSnapshotBuilder()

    def evaluate(self, execution_context: PortfolioDecisionExecutionContext) -> PortfolioDecisionSnapshot:
        # 1. Structural Validation
        self._structural_rules.validate(execution_context)

        # 2. Consistency Validation
        self._consistency_rules.validate(execution_context)

        # Initialize Pipeline Context
        execution_id = str(uuid.uuid4())
        pipeline_context = PortfolioDecisionPipelineContext(
            execution_context=execution_context,
            execution_id=execution_id
        )

        # 3. & 4. Pipeline Execution (Aggregation -> Rules)
        for stage in self._pipeline_stages:
            pipeline_context = stage.execute(pipeline_context)

        # 5. Snapshot Construction
        snapshot = self._builder.build(pipeline_context)

        # 6. Persistence
        self._repository.save(snapshot)

        return snapshot
