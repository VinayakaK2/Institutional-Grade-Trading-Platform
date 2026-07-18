import time
import tracemalloc
from typing import Dict, Any
from backend.trade_validation_engine.certification.contracts.stage import ICertificationStage
from backend.trade_validation_engine.certification.config.config import CertificationConfig
from backend.trade_validation_engine.certification.models.models import StageResult

class StressVerificationStage(ICertificationStage):
    @property
    def stage_name(self) -> str:
        return "Stress"

    async def execute(self, config: CertificationConfig, context: Dict[str, Any]) -> StageResult:
        start_t = time.time()
        
        engine = context.get("optimization_engine")
        if not engine:
            return StageResult(stage_name=self.stage_name, status="SKIP", duration_ms=0, metrics={})
            
        base_dataset = context.get("functional_dataset", [])
        if not base_dataset:
            return StageResult(stage_name=self.stage_name, status="SKIP", duration_ms=0, metrics={"reason": "No base dataset"})
            
        tracemalloc.start()
        
        mem_growths = []
        total_snapshots = 0
        
        for batch_size in config.stress_batch_sizes:
            # Generate stress batch by cycling the base dataset
            stress_dataset = [base_dataset[i % len(base_dataset)] for i in range(batch_size)]
            
            # GC collect implicitly tracked by tracemalloc baseline
            snapshot1 = tracemalloc.take_snapshot()
            
            results = await engine.execute_batch(stress_dataset)
            total_snapshots += len(results)
            
            snapshot2 = tracemalloc.take_snapshot()
            
            # Compare memory
            stats = snapshot2.compare_to(snapshot1, 'lineno')
            growth_bytes = sum(stat.size_diff for stat in stats)
            growth_mb = growth_bytes / (1024 * 1024)
            mem_growths.append(growth_mb)
            
            if growth_mb > config.allowed_memory_growth_mb:
                tracemalloc.stop()
                return StageResult(
                    stage_name=self.stage_name,
                    status="FAIL",
                    duration_ms=int((time.time() - start_t) * 1000),
                    metrics={"reason": "Memory leak detected", "growth_mb": growth_mb}
                )
        
        tracemalloc.stop()
        
        duration = int((time.time() - start_t) * 1000)
        
        context["evidence"] = {
            "total_snapshots": total_snapshots,
            "memory_growths_mb": mem_growths
        }
        
        context["snapshot_count"] = total_snapshots
        context["peak_memory_mb"] = max(mem_growths) if mem_growths else 0.0
        
        return StageResult(
            stage_name=self.stage_name,
            status="PASS",
            duration_ms=duration,
            metrics={"max_growth_mb": max(mem_growths) if mem_growths else 0.0}
        )
