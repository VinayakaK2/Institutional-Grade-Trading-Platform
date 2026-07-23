import pytest
from backend.paper_fill_engine.core.lifecycle import PaperFillLifecycleManager
from backend.paper_fill_engine.models.fill import FillState
from backend.paper_fill_engine.exceptions.exceptions import PaperFillTransitionError

def test_lifecycle_manager_valid_transitions():
    PaperFillLifecycleManager.validate_transition(FillState.PENDING_FILL, FillState.PARTIALLY_FILLED)
    PaperFillLifecycleManager.validate_transition(FillState.PENDING_FILL, FillState.FILLED)
    PaperFillLifecycleManager.validate_transition(FillState.PENDING_FILL, FillState.EXPIRED)
    
    PaperFillLifecycleManager.validate_transition(FillState.PARTIALLY_FILLED, FillState.PARTIALLY_FILLED)
    PaperFillLifecycleManager.validate_transition(FillState.PARTIALLY_FILLED, FillState.FILLED)
    PaperFillLifecycleManager.validate_transition(FillState.PARTIALLY_FILLED, FillState.EXPIRED)

def test_lifecycle_manager_invalid_transitions():
    with pytest.raises(PaperFillTransitionError):
        PaperFillLifecycleManager.validate_transition(FillState.FILLED, FillState.PARTIALLY_FILLED)
        
    with pytest.raises(PaperFillTransitionError):
        PaperFillLifecycleManager.validate_transition(FillState.EXPIRED, FillState.PENDING_FILL)

def test_lifecycle_manager_is_terminal():
    assert PaperFillLifecycleManager.is_terminal(FillState.FILLED)
    assert PaperFillLifecycleManager.is_terminal(FillState.EXPIRED)
    
    assert not PaperFillLifecycleManager.is_terminal(FillState.PENDING_FILL)
    assert not PaperFillLifecycleManager.is_terminal(FillState.PARTIALLY_FILLED)
