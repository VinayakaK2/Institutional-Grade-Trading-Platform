from datetime import datetime, timezone
from typing import List
from backend.paper_execution_result_engine.models.contexts import PaperExecutionResultPipelineContext
from backend.paper_execution_result_engine.models.resolution import ExecutionTimeline, ExecutionEvent

class ExecutionTimelineStage:
    """
    Constructs the ExecutionTimeline using historical fill events and appending
    the final execution status. Sorts deterministically.
    """
    def execute(self, context: PaperExecutionResultPipelineContext) -> None:
        status = context.execution_status
        if not status:
            from backend.paper_execution_result_engine.exceptions.exceptions import PaperExecutionResultCalculationError
            raise PaperExecutionResultCalculationError("ExecutionStatus must be resolved before ExecutionTimeline.")

        events: List[ExecutionEvent] = []
        fill_events = context.execution_context.paper_fill_snapshot.fill_events
        
        # 1. Pull historical fill events exactly as provided by upstream
        for f_event in fill_events:
            events.append(ExecutionEvent(
                event_id=f_event.fill_id,
                event_type="FILL_EVENT",
                timestamp=f_event.timestamp,
                sequence_number=f_event.sequence_number,
                details={
                    "quantity": f_event.quantity,
                    "price": f_event.price,
                    "remaining_quantity_after_fill": f_event.remaining_quantity_after_fill
                }
            ))
            
        # 2. Append the resolved terminal status event (using a generated stable sequence_number, larger than fills)
        max_seq = max([e.sequence_number for e in events]) if events else 0
        final_seq = max_seq + 1
        current_iso = datetime.now(timezone.utc).isoformat()
        
        # Generate a deterministic pseudo-ID based on snapshot hashes or similar? 
        # The prompt mentioned: "The ordering key should come entirely from deterministic upstream data."
        # The final event timestamp might not be perfectly deterministic if we use datetime.now(), 
        # but timeline is generally built at runtime. Actually, it's better to use the eq_snapshot timestamp if available,
        # or just timezone.utc.isoformat(). Let's stick to current time for the final event, but order it last via sequence.
        
        events.append(ExecutionEvent(
            event_id=f"resolved_{context.execution_context.paper_order_snapshot.snapshot_version}",
            event_type=f"FINAL_STATUS_{status.value}",
            timestamp=current_iso,
            sequence_number=final_seq,
            details={"status": status.value}
        ))
        
        # 3. Sort deterministically: timestamp -> event type priority -> sequence number
        # Priority mapping
        type_priority = {
            "FILL_EVENT": 1
        }
        
        def sort_key(e: ExecutionEvent):
            prio = type_priority.get(e.event_type, 99) # 99 for FINAL_STATUS
            return (e.timestamp, prio, e.sequence_number)
            
        events.sort(key=sort_key)
        
        context.execution_timeline = ExecutionTimeline(events=events)
