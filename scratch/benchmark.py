import asyncio
import time
from typing import List

from backend.watchlist_engine.models.models import WatchlistCandidate, WatchlistSymbol, WatchlistExecutionContext, WatchlistSnapshot, WatchlistStageResult, WatchlistStageStatus
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.optimization.pipeline import OptimizedWatchlistPipeline
from backend.watchlist_engine.models.config import WatchlistOptimizationSettings
from backend.watchlist_engine.optimization.fingerprint import OptimizationFingerprintBuilder

class MockInnerPipeline:
    async def execute(self, context: WatchlistExecutionContext) -> WatchlistExecutionContext:
        # Simulate processing time for each candidate
        await asyncio.sleep(0.01 * len(context.candidates))
        context.stage_results = [
            WatchlistStageResult(
                stage_name="MockStage",
                status=WatchlistStageStatus.SUCCESS,
                duration_ms=10.0 * len(context.candidates)
            )
        ]
        return context

class MockRepository:
    def __init__(self, prev_candidates=None):
        self.prev_candidates = prev_candidates or []
        
    async def load_latest_snapshot(self):
        if not self.prev_candidates:
            return None
            
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        return WatchlistSnapshot(
            snapshot_id="snap0",
            version=1,
            created_at=now,
            symbol_count=len(self.prev_candidates),
            pipeline_version="1.0.0",
            config_hash="hash1",
            validation_status="PASSED",
            candidates=self.prev_candidates,
            metadata={}
        )

def generate_candidates(count: int, offset: int = 0) -> List[WatchlistCandidate]:
    candidates = []
    for i in range(count):
        candidates.append(
            WatchlistCandidate(
                watchlist_symbol=WatchlistSymbol(
                    symbol=SymbolReference(symbol=f"SYM{i+offset}", exchange=ExchangeReference(code="US")),
                    market_segment="US",
                    is_certified=True
                )
            )
        )
    return candidates

async def run_benchmark():
    scenarios = [100, 500, 1000]
    
    print("Optimization Engine Performance Benchmark\n")
    print("-" * 50)
    
    for count in scenarios:
        # Generate new candidates
        candidates = generate_candidates(count)
        # Previous snapshot has exactly the same candidates, but let's change 5% of them
        # so reuse percentage is 95%
        num_changed = max(1, int(count * 0.05))
        prev_candidates = candidates[:-num_changed] + generate_candidates(num_changed, offset=count*10)
        
        # Test 1: Original Execution (No optimization)
        # Sequential processing, 100% processing
        mock_inner = MockInnerPipeline()
        mock_repo = MockRepository(prev_candidates=None)
        
        settings_unopt = WatchlistOptimizationSettings(
            enable_incremental_processing=False,
            enable_parallel_execution=False
        )
        
        pipeline_unopt = OptimizedWatchlistPipeline(mock_inner, settings_unopt, mock_repo)
        
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        ctx_unopt = WatchlistExecutionContext(
            run_id="run_unopt",
            snapshot_id="snap1",
            started_at=now,
            candidates=candidates,
            metadata={"config_hash": "hash1"}
        )
        
        t0 = time.perf_counter()
        await pipeline_unopt.execute(ctx_unopt)
        time_unopt = (time.perf_counter() - t0) * 1000
        
        
        # Test 2: Optimized Execution (Parallel + Incremental)
        mock_inner_opt = MockInnerPipeline()
        mock_repo_opt = MockRepository(prev_candidates=prev_candidates)
        
        settings_opt = WatchlistOptimizationSettings(
            enable_incremental_processing=True,
            enable_parallel_execution=True,
            max_parallel_workers=10,
            batch_size=100
        )
        
        pipeline_opt = OptimizedWatchlistPipeline(mock_inner_opt, settings_opt, mock_repo_opt)
        
        ctx_opt = WatchlistExecutionContext(
            run_id="run_opt",
            snapshot_id="snap2",
            started_at=now,
            candidates=candidates,
            metadata={"config_hash": "hash1"}
        )
        
        t0 = time.perf_counter()
        res_opt = await pipeline_opt.execute(ctx_opt)
        time_opt = (time.perf_counter() - t0) * 1000
        
        reuse_pct = res_opt.metadata["optimization_stats"]["reuse_percentage"]
        
        print(f"Candidates: {count}")
        print(f"Original Execution Time: {time_unopt:.2f} ms")
        print(f"Optimized Execution Time: {time_opt:.2f} ms")
        print(f"Reuse Percentage: {reuse_pct:.1f}%")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
