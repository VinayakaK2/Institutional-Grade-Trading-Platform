from backend.paper_order_engine.models.order import OrderState
from backend.paper_order_engine.exceptions.exceptions import PaperOrderTransitionError
from typing import Set, Dict

class PaperOrderLifecycleManager:
    """
    Centralized manager for legal order state transitions.
    """
    # Define valid transitions FROM a state TO a set of allowed states
    _allowed_transitions: Dict[OrderState, Set[OrderState]] = {
        OrderState.CREATED: {OrderState.ACCEPTED, OrderState.REJECTED, OrderState.CANCELLED, OrderState.EXPIRED},
        OrderState.ACCEPTED: {OrderState.PENDING, OrderState.CANCELLED},
        OrderState.PENDING: {OrderState.CANCELLED, OrderState.EXPIRED},
        
        # Terminal states have no valid outgoing transitions
        OrderState.CANCELLED: set(),
        OrderState.REJECTED: set(),
        OrderState.EXPIRED: set()
    }

    @classmethod
    def validate_transition(cls, current_state: OrderState, next_state: OrderState) -> None:
        """
        Validates if transitioning from current_state to next_state is legal.
        Raises PaperOrderTransitionError if the transition is illegal.
        """
        if current_state not in cls._allowed_transitions:
            raise PaperOrderTransitionError(f"Unknown current state: {current_state}")
            
        if next_state not in cls._allowed_transitions[current_state]:
            raise PaperOrderTransitionError(
                f"Illegal state transition from {current_state.value} to {next_state.value}"
            )

    @classmethod
    def is_terminal(cls, state: OrderState) -> bool:
        """
        Returns True if the state is terminal (no further transitions allowed).
        """
        return state in {OrderState.CANCELLED, OrderState.REJECTED, OrderState.EXPIRED}
