import logging
from typing import List
from backend.liquidity_grab_engine.lifecycle.contracts.evidence import (
    IEvidenceStrategy,
    IContinuationStrategy,
    IWeakeningStrategy,
    IFailureStrategy,
    IExpirationStrategy
)
from backend.liquidity_grab_engine.lifecycle.models.context import LiquidityGrabLifecycleContext
from backend.liquidity_grab_engine.lifecycle.models.models import LifecycleEvidence

logger = logging.getLogger(__name__)

class EvidenceRegistry:
    def __init__(self) -> None:
        self._continuation_strategies: List[IContinuationStrategy] = []
        self._weakening_strategies: List[IWeakeningStrategy] = []
        self._failure_strategies: List[IFailureStrategy] = []
        self._expiration_strategies: List[IExpirationStrategy] = []
        
    def register_continuation(self, strategy: IContinuationStrategy) -> None:
        self._continuation_strategies.append(strategy)
        
    def register_weakening(self, strategy: IWeakeningStrategy) -> None:
        self._weakening_strategies.append(strategy)
        
    def register_failure(self, strategy: IFailureStrategy) -> None:
        self._failure_strategies.append(strategy)
        
    def register_expiration(self, strategy: IExpirationStrategy) -> None:
        self._expiration_strategies.append(strategy)

    def execute(self, context: LiquidityGrabLifecycleContext) -> LifecycleEvidence:
        logger.info("Executing lifecycle evidence strategies.")
        
        # Sort all lists by ascending priority, then ascending strategy_id for deterministic execution
        def sort_key(s: IEvidenceStrategy) -> tuple:
            return (s.priority, s.strategy_id)
            
        cont_strats = sorted(self._continuation_strategies, key=sort_key)
        weak_strats = sorted(self._weakening_strategies, key=sort_key)
        fail_strats = sorted(self._failure_strategies, key=sort_key)
        exp_strats = sorted(self._expiration_strategies, key=sort_key)

        best_cont = None
        for c_strat in cont_strats:
            c_ev = c_strat.evaluate(context)
            if best_cont is None or c_ev.confidence > best_cont.confidence:
                best_cont = c_ev
                
        best_weak = None
        for w_strat in weak_strats:
            w_ev = w_strat.evaluate(context)
            if best_weak is None or w_ev.confidence > best_weak.confidence:
                best_weak = w_ev
                
        best_fail = None
        for f_strat in fail_strats:
            f_ev = f_strat.evaluate(context)
            if best_fail is None or f_ev.confidence > best_fail.confidence:
                best_fail = f_ev
                
        best_exp = None
        for e_strat in exp_strats:
            e_ev = e_strat.evaluate(context)
            if best_exp is None or e_ev.confidence > best_exp.confidence:
                best_exp = e_ev
                
        return LifecycleEvidence(
            continuation_evidence=best_cont,
            weakening_evidence=best_weak,
            failure_evidence=best_fail,
            expiration_evidence=best_exp
        )
