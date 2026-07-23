import uuid
from datetime import datetime, timezone
from backend.paper_fill_engine.contracts.pipeline import IPaperFillPipelineStage
from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext, PaperFillPipelineContext, FillSimulationResult
from backend.paper_fill_engine.models.fill import FillState
from backend.paper_fill_engine.models.events import FillEvent
from backend.paper_fill_engine.exceptions.exceptions import PaperFillSimulationError
from backend.paper_fill_engine.core.lifecycle import PaperFillLifecycleManager

class DeterministicFillStage(IPaperFillPipelineStage):
    """
    Simulates fills deterministically based on configuration.
    Outputs a single FillSimulationResult.
    """
    async def execute(self, execution_context: PaperFillExecutionContext, pipeline_context: PaperFillPipelineContext) -> None:
        cfg = execution_context.configuration
        requested_quantity = cfg.get("requested_quantity", 0)
        
        if requested_quantity <= 0:
            raise PaperFillSimulationError("Requested quantity must be strictly positive.")
            
        fills = cfg.get("simulated_fills", [])
        
        events = []
        total_filled = 0
        avg_price = None
        
        fill_ids = set()
        seq_numbers = set()
        
        # Sort incoming config fills by sequence number if provided, else assign sequential
        for idx, f in enumerate(fills):
            if "sequence_number" not in f:
                f["sequence_number"] = idx + 1
                
        fills = sorted(fills, key=lambda x: x["sequence_number"])
        
        expected_seq = 1
        
        for f in fills:
            fq = f.get("quantity", 0)
            fp = f.get("price", 0.0)
            fid = f.get("fill_id", str(uuid.uuid4()))
            fseq = f.get("sequence_number")
            
            if fq <= 0 or fp <= 0.0:
                raise PaperFillSimulationError(f"Invalid fill quantity ({fq}) or price ({fp}).")
                
            if fid in fill_ids:
                raise PaperFillSimulationError(f"Duplicate fill ID encountered: {fid}")
            fill_ids.add(fid)
            
            if fseq in seq_numbers:
                raise PaperFillSimulationError(f"Duplicate sequence number encountered: {fseq}")
            if fseq != expected_seq:
                raise PaperFillSimulationError(f"Sequence gap detected. Expected {expected_seq}, got {fseq}")
            seq_numbers.add(fseq)
            expected_seq += 1
                
            if total_filled + fq > requested_quantity:
                raise PaperFillSimulationError(f"Overfill protection: attempt to fill {total_filled + fq} > requested {requested_quantity}")
                
            total_filled += fq
            rem_qty = requested_quantity - total_filled
            
            events.append(FillEvent(
                fill_id=fid,
                quantity=fq,
                price=fp,
                timestamp=f.get("timestamp", datetime.now(timezone.utc).isoformat()),
                sequence_number=fseq,
                remaining_quantity_after_fill=rem_qty
            ))
            
        if total_filled > 0:
            avg_price = sum(e.quantity * e.price for e in events) / total_filled

        # Determine Fill State
        if total_filled == 0:
            # We assume it remains PENDING_FILL if no fills happened but it's valid
            state = FillState.PENDING_FILL
        elif total_filled < requested_quantity:
            state = FillState.PARTIALLY_FILLED
        else:
            state = FillState.FILLED

        pipeline_context.simulation_result = FillSimulationResult(
            fill_state=state,
            fill_events=events,
            total_filled_quantity=total_filled,
            remaining_quantity=requested_quantity - total_filled,
            average_fill_price=avg_price
        )

class LifecycleValidationStage(IPaperFillPipelineStage):
    """
    Validates state transitions of the simulated result.
    Assumes previous state is PENDING_FILL for a new fill simulation pipeline run, 
    but for a robust FSM, we might pass in current state. Here we validate 
    from PENDING_FILL -> target state.
    """
    async def execute(self, execution_context: PaperFillExecutionContext, pipeline_context: PaperFillPipelineContext) -> None:
        if not pipeline_context.simulation_result:
            raise PaperFillSimulationError("No simulation result available for lifecycle validation.")
            
        # For this engine, we assume the initial state before fills is PENDING_FILL.
        # In a real event-sourced system, we would load the last known state.
        # Here we just validate that PENDING_FILL can transition to the new state.
        target_state = pipeline_context.simulation_result.fill_state
        
        # It's perfectly legal to remain in PENDING_FILL if no fills were generated.
        if target_state != FillState.PENDING_FILL:
            PaperFillLifecycleManager.validate_transition(FillState.PENDING_FILL, target_state)
