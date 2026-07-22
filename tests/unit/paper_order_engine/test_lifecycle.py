import pytest
from backend.paper_order_engine.core.lifecycle import PaperOrderLifecycleManager
from backend.paper_order_engine.models.order import OrderState
from backend.paper_order_engine.exceptions.exceptions import PaperOrderTransitionError

def test_lifecycle_manager_valid_transitions():
    PaperOrderLifecycleManager.validate_transition(OrderState.CREATED, OrderState.ACCEPTED)
    PaperOrderLifecycleManager.validate_transition(OrderState.CREATED, OrderState.REJECTED)
    PaperOrderLifecycleManager.validate_transition(OrderState.CREATED, OrderState.CANCELLED)
    PaperOrderLifecycleManager.validate_transition(OrderState.CREATED, OrderState.EXPIRED)
    
    PaperOrderLifecycleManager.validate_transition(OrderState.ACCEPTED, OrderState.PENDING)
    PaperOrderLifecycleManager.validate_transition(OrderState.ACCEPTED, OrderState.CANCELLED)
    
    PaperOrderLifecycleManager.validate_transition(OrderState.PENDING, OrderState.CANCELLED)
    PaperOrderLifecycleManager.validate_transition(OrderState.PENDING, OrderState.EXPIRED)

def test_lifecycle_manager_invalid_transitions():
    with pytest.raises(PaperOrderTransitionError):
        PaperOrderLifecycleManager.validate_transition(OrderState.REJECTED, OrderState.ACCEPTED)
        
    with pytest.raises(PaperOrderTransitionError):
        PaperOrderLifecycleManager.validate_transition(OrderState.CANCELLED, OrderState.PENDING)
        
    with pytest.raises(PaperOrderTransitionError):
        PaperOrderLifecycleManager.validate_transition(OrderState.ACCEPTED, OrderState.CREATED)

def test_lifecycle_manager_is_terminal():
    assert PaperOrderLifecycleManager.is_terminal(OrderState.CANCELLED)
    assert PaperOrderLifecycleManager.is_terminal(OrderState.REJECTED)
    assert PaperOrderLifecycleManager.is_terminal(OrderState.EXPIRED)
    
    assert not PaperOrderLifecycleManager.is_terminal(OrderState.CREATED)
    assert not PaperOrderLifecycleManager.is_terminal(OrderState.ACCEPTED)
    assert not PaperOrderLifecycleManager.is_terminal(OrderState.PENDING)
