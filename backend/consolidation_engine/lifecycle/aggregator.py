from typing import List
from backend.consolidation_engine.lifecycle.models import (
    ConsolidationLifecycleState,
    BaseLifecycleEvidence,
    EndEvidence,
    BreakEvidence,
    WeakeningEvidence,
    ContinuationEvidence
)
from backend.consolidation_engine.lifecycle.config import ConsolidationLifecycleConfiguration

class LifecycleAggregator:
    """
    Deterministically aggregates lifecycle evidence to produce a final state.
    Contains no business logic, applies precedence rules strictly based on triggered evidence.
    """
    
    @staticmethod
    def resolve_state(
        evidence_list: List[BaseLifecycleEvidence], 
        config: ConsolidationLifecycleConfiguration
    ) -> ConsolidationLifecycleState:
        
        # We need to map Evidence types to State strings based on config precedence.
        # This is a fixed mapping for the Phase 8.4 engine boundaries.
        evidence_state_map = {
            EndEvidence: ConsolidationLifecycleState.ENDED,
            BreakEvidence: ConsolidationLifecycleState.BROKEN,
            WeakeningEvidence: ConsolidationLifecycleState.WEAKENING,
            ContinuationEvidence: ConsolidationLifecycleState.CONTINUING
        }
        
        # Check triggered evidence
        triggered_states = []
        for ev in evidence_list:
            if ev.triggered:
                # Find corresponding state
                for ev_type, state in evidence_state_map.items():
                    if isinstance(ev, ev_type):
                        triggered_states.append(state.value)
                        break
        
        if not triggered_states:
            return ConsolidationLifecycleState.ACTIVE
            
        # Apply deterministic precedence from config
        # config.state_precedence is ordered from highest to lowest precedence
        # e.g., ["ENDED", "BROKEN", "WEAKENING", "CONTINUING", "ACTIVE"]
        for p_state in config.state_precedence:
            if p_state in triggered_states:
                return ConsolidationLifecycleState(p_state)
                
        return ConsolidationLifecycleState.ACTIVE
