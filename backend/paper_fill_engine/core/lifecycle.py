from typing import Dict, Set
from backend.paper_fill_engine.models.fill import FillState
from backend.paper_fill_engine.exceptions.exceptions import PaperFillTransitionError

class PaperFillLifecycleManager:
    """
    Centralized, data-driven manager for legal fill state transitions.
    """
    ALLOWED_TRANSITIONS: Dict[FillState, Set[FillState]] = {
        FillState.PENDING_FILL: {FillState.PARTIALLY_FILLED, FillState.FILLED, FillState.EXPIRED},
        FillState.PARTIALLY_FILLED: {FillState.PARTIALLY_FILLED, FillState.FILLED, FillState.EXPIRED},
        FillState.FILLED: set(),
        FillState.EXPIRED: set()
    }

    @classmethod
    def validate_transition(cls, current_state: FillState, next_state: FillState) -> None:
        """
        Validates if transitioning from current_state to next_state is legal.
        Raises PaperFillTransitionError if the transition is illegal.
        """
        if current_state not in cls.ALLOWED_TRANSITIONS:
            raise PaperFillTransitionError(f"Unknown current state: {current_state}")
            
        if next_state not in cls.ALLOWED_TRANSITIONS[current_state]:
            raise PaperFillTransitionError(
                f"Illegal fill state transition from {current_state.value} to {next_state.value}"
            )

    @classmethod
    def is_terminal(cls, state: FillState) -> bool:
        """
        Returns True if the state is terminal (no further transitions allowed).
        """
        return state in {FillState.FILLED, FillState.EXPIRED}
