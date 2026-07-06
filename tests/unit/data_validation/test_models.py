import pytest
from backend.data_validation.models.state import DataState

def test_data_state_enum():
    assert DataState.UNVALIDATED.value == "UNVALIDATED"
    assert DataState.VALIDATING.value == "VALIDATING"
    assert DataState.VALIDATED.value == "VALIDATED"
    assert DataState.CLEANING.value == "CLEANING"
    assert DataState.CLEANED.value == "CLEANED"
    assert DataState.CERTIFIED.value == "CERTIFIED"
    assert DataState.CANONICAL.value == "CANONICAL"
    assert DataState.QUARANTINED.value == "QUARANTINED"
