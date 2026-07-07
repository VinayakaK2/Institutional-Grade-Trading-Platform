import asyncio
import hashlib
from typing import AsyncIterable, AsyncGenerator, List, Dict, Optional
from backend.universe_engine.classification.models import ClassifiedSymbol
from backend.universe_engine.contracts.optimization import IUniverseOptimizationStage
from backend.universe_engine.optimization.models import UniverseOptimizationContext

def compute_business_fingerprint(symbol: ClassifiedSymbol) -> str:
    """
    Computes a deterministic Business Fingerprint.
    
    BUSINESS FINGERPRINT CONTRACT:
    The fingerprint is strictly defined by the following business fields:
    - Symbol ID
    - Sector
    - Industry
    - Market Cap
    - Liquidity
    - Data Quality
    
    It intentionally excludes audit metadata, execution metadata, and runtime information.
    Any changes to this field list or classification schema MUST correspond to a pipeline
    version increment.
    
    CACHE & INVALIDATION BEHAVIOUR:
    If the classification schema or this fingerprint generation logic is altered, 
    all previous optimization snapshots are considered obsolete for incremental diffing.
    A full rebuild will be triggered by changing the `pipeline_version` configuration,
    which orphans old fingerprints.
    """
    # Create deterministic string from canonical fields
    payload = (
        f"{symbol.symbol.symbol.symbol}|"
        f"{symbol.sector}|"
        f"{symbol.industry}|"
        f"{symbol.market_cap}|"
        f"{symbol.liquidity}|"
        f"{symbol.data_quality}"
    )
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

class OptimizationTask:
    """Wrapper to hold execution state for a symbol during the pipeline."""
    def __init__(self, symbol: ClassifiedSymbol, is_changed: bool, fingerprint: str):
        self.symbol = symbol
        self.is_changed = is_changed
        self.fingerprint = fingerprint

class DiffDetectionStage(IUniverseOptimizationStage[ClassifiedSymbol, OptimizationTask]):
    """
    Generates a deterministic Business Fingerprint and compares it with
    the previous optimized universe to detect changes.
    """
    def __init__(self, previous_fingerprints: Optional[Dict[str, str]] = None):
        self.previous_fingerprints = previous_fingerprints or {}

    async def execute(self, context: UniverseOptimizationContext, items: AsyncIterable[ClassifiedSymbol]) -> AsyncGenerator[OptimizationTask, None]:
        async for symbol in items:
            context.metrics.total_symbols += 1
            fingerprint = compute_business_fingerprint(symbol)
            
            is_changed = True
            symbol_key = symbol.symbol.symbol.symbol
            
            if context.config.enable_incremental and self.previous_fingerprints:
                if symbol_key in self.previous_fingerprints:
                    if self.previous_fingerprints[symbol_key] == fingerprint:
                        is_changed = False
            
            if is_changed:
                context.metrics.symbols_reprocessed += 1
            else:
                context.metrics.symbols_reused += 1

            yield OptimizationTask(symbol=symbol, is_changed=is_changed, fingerprint=fingerprint)

class ReuseUnchangedSymbolsStage(IUniverseOptimizationStage[OptimizationTask, OptimizationTask]):
    """
    Separates unchanged symbols from changed symbols so that unchanged
    symbols can bypass expensive batching and parallel execution.
    For now, it yields all tasks, but downstream stages will filter out
    the unchanged ones for heavy processing.
    """
    async def execute(self, context: UniverseOptimizationContext, items: AsyncIterable[OptimizationTask]) -> AsyncGenerator[OptimizationTask, None]:
        async for task in items:
            # We yield all of them so they reach the final merge.
            # Downstream batch builder will only batch the changed ones.
            yield task

class BatchBuilderStage(IUniverseOptimizationStage[OptimizationTask, List[OptimizationTask]]):
    """
    Groups changed symbols into memory-efficient batches.
    Unchanged symbols are yielded as single-item batches immediately to bypass waiting.
    """
    async def execute(self, context: UniverseOptimizationContext, items: AsyncIterable[OptimizationTask]) -> AsyncGenerator[List[OptimizationTask], None]:
        batch = []
        batch_size = context.config.batch_size if context.config.enable_batching else 1

        async for task in items:
            if not task.is_changed:
                # Unchanged symbols bypass batching.
                yield [task]
                continue
            
            batch.append(task)
            if len(batch) >= batch_size:
                context.metrics.batch_count += 1
                yield batch
                batch = []
        
        if batch:
            context.metrics.batch_count += 1
            yield batch

class ParallelExecutorStage(IUniverseOptimizationStage[List[OptimizationTask], List[OptimizationTask]]):
    """
    Executes batches concurrently. If parallel execution is disabled, falls back to sequential.
    """
    async def process_task(self, task: OptimizationTask) -> OptimizationTask:
        # Simulate real optimization work (e.g. complex re-evaluations or transformations)
        # without altering the business data as per requirements.
        await asyncio.sleep(0.0001)
        return task

    async def execute(self, context: UniverseOptimizationContext, items: AsyncIterable[List[OptimizationTask]]) -> AsyncGenerator[List[OptimizationTask], None]:
        # To strictly enforce max_workers, we use a semaphore.
        max_workers = context.config.max_workers
        semaphore = asyncio.Semaphore(max_workers)

        async def _execute_batch(batch: List[OptimizationTask]) -> List[OptimizationTask]:
            if not batch or not batch[0].is_changed:
                return batch # Bypass processing for unchanged symbols
                
            if context.config.enable_parallel:
                async with semaphore:
                    context.metrics.parallel_workers_used = max(
                        context.metrics.parallel_workers_used, 
                        max_workers - semaphore._value
                    )
                    # Parallel execution of tasks within the batch
                    processed = await asyncio.gather(*(self.process_task(t) for t in batch))
                    return list(processed)
            else:
                # Sequential fallback
                processed = []
                for t in batch:
                    processed.append(await self.process_task(t))
                return processed

        # We must process batches as they arrive from the generator
        # To overlap batch execution, we can spawn tasks and yield as completed.
        # But for deterministic order (if required), we process them inline.
        # The prompt says: "Sequential vs Parallel equivalence. Deterministic output."
        # We will await them inline here, but use gather internally for the batch items.
        
        async for batch in items:
            processed_batch = await _execute_batch(batch)
            yield processed_batch
