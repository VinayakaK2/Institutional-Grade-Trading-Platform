from typing import AsyncIterable, Optional, Dict
from backend.universe_engine.classification.models import ClassifiedSymbol
from backend.universe_engine.optimization.models import UniverseOptimizationContext
from backend.universe_engine.optimization.stages import (
    DiffDetectionStage,
    ReuseUnchangedSymbolsStage,
    BatchBuilderStage,
    ParallelExecutorStage,
    OptimizationTask
)

class UniverseOptimizationPipeline:
    """
    Orchestrates the optimization stages lazily.
    Maintains a maximum of 1 active working copy via async generators.
    """
    
    async def execute(
        self, 
        context: UniverseOptimizationContext, 
        symbols: AsyncIterable[ClassifiedSymbol],
        previous_fingerprints: Optional[Dict[str, str]] = None
    ) -> AsyncIterable[OptimizationTask]:
        """
        Executes the optimization pipeline. Returns an async iterable of OptimizationTasks
        which can be merged by the engine into the final output.
        """
        
        diff_stage = DiffDetectionStage(previous_fingerprints)
        reuse_stage = ReuseUnchangedSymbolsStage()
        batch_stage = BatchBuilderStage()
        exec_stage = ParallelExecutorStage()
        
        # 1. Diff Detection
        stream_1 = diff_stage.execute(context, symbols)
        
        # 2. Reuse Unchanged Symbols
        stream_2 = reuse_stage.execute(context, stream_1)
        
        # 3. Batch Builder
        stream_3 = batch_stage.execute(context, stream_2)
        
        # 4. Parallel Executor
        stream_4 = exec_stage.execute(context, stream_3)
        
        # 5. Merge Results (flattening the batches back to a single stream)
        async for batch in stream_4:
            for task in batch:
                yield task
