from backend.paper_execution_result_engine.core.engine import PaperExecutionResultEngine
from backend.paper_execution_result_engine.models.resolution import ExecutionStatus

def test_engine_execution(mock_execution_context):
    engine = PaperExecutionResultEngine()
    snapshot = engine.execute(mock_execution_context)
    
    assert snapshot is not None
    assert snapshot.execution_status == ExecutionStatus.EXECUTED
    assert snapshot.execution_summary.filled_quantity == 100
    assert len(snapshot.execution_timeline.events) == 2
    assert snapshot.business_fingerprint is not None
    
def test_engine_fingerprint_differs_on_status(mock_execution_context):
    engine = PaperExecutionResultEngine()
    snap1 = engine.execute(mock_execution_context)
    
    bad_order = mock_execution_context.paper_order_snapshot.model_copy(update={"order_state": "REJECTED"})
    exec_context = mock_execution_context.model_copy(update={"paper_order_snapshot": bad_order})
    snap2 = engine.execute(exec_context)
    
    assert snap1.business_fingerprint != snap2.business_fingerprint
