import time
from typing import Dict, Any
from backend.trade_validation_engine.certification.contracts.stage import ICertificationStage
from backend.trade_validation_engine.certification.config.config import CertificationConfig
from backend.trade_validation_engine.certification.models.models import StageResult

class PerformanceVerificationStage(ICertificationStage):
    @property
    def stage_name(self) -> str:
        return "Performance"

    async def execute(self, config: CertificationConfig, context: Dict[str, Any]) -> StageResult:
        start_t = time.time()
        
        engine = context.get("optimization_engine")
        if not engine:
            return StageResult(stage_name=self.stage_name, status="SKIP", duration_ms=0, metrics={})
            
        dataset = context.get("functional_dataset", [])
        if not dataset:
            return StageResult(stage_name=self.stage_name, status="SKIP", duration_ms=0, metrics={})
            
        # Run iterations
        throughputs = []
        for _ in range(config.performance_iterations):
            iter_start = time.time()
            res = await engine.execute_batch(dataset)
            iter_end = time.time()
            iter_dur = iter_end - iter_start
            
            if iter_dur > 0:
                throughputs.append(len(res) / iter_dur)
                
        duration = int((time.time() - start_t) * 1000)
        
        avg_throughput = sum(throughputs) / len(throughputs) if throughputs else 0
        
        context["evidence"] = {
            "iterations": config.performance_iterations,
            "average_throughput_per_sec": avg_throughput
        }
        
        # Informational only, never fail
        return StageResult(
            stage_name=self.stage_name,
            status="PASS",
            duration_ms=duration,
            metrics={"avg_throughput": avg_throughput}
        )
