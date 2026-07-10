"""
Trend Quality Engine
====================

Orchestrates the evaluation of a detected trend's structural quality.
"""

import time
import uuid
import hashlib
import json
from datetime import datetime, timezone
from typing import List, cast

from backend.trend_engine.quality.contracts.contracts import (
    ITrendQualityEngine, 
    ITrendQualityRepository, 
    ITrendQualityStage
)
from backend.trend_engine.quality.config.config import TrendQualityConfig
from backend.trend_engine.models.models import TrendSnapshot
from backend.trend_engine.quality.models.models import (
    TrendQualitySnapshot,
    TrendQualitySymbolResult,
    NormalizedQualityMetrics,
    TrendStrengthResult,
    TrendConsistencyResult,
    PullbackQualityResult,
    TrendPersistenceResult,
    TrendQualityMetadata
)
from backend.trend_engine.quality.pipeline.context import QualityExecutionContext
from backend.trend_engine.quality.pipeline.pipeline import TrendQualityPipeline
from backend.trend_engine.quality.exceptions import IncompleteQualityEvaluationError


class TrendQualityEngine(ITrendQualityEngine):
    """
    Evaluates Trend Quality objectively and deterministically.
    """
    
    def __init__(
        self,
        repository: ITrendQualityRepository,
        config: TrendQualityConfig,
        stages: List[ITrendQualityStage]
    ):
        self._repository = repository
        self._config = config
        self._pipeline = TrendQualityPipeline(stages)
        
    def _generate_config_hash(self) -> str:
        # Deterministic hashing of the configuration
        cfg_dict = self._config.model_dump()
        cfg_str = json.dumps(cfg_dict, sort_keys=True)
        return hashlib.sha256(cfg_str.encode('utf-8')).hexdigest()
        
    async def evaluate_trend_quality(self, parent_snapshot: TrendSnapshot) -> TrendQualitySnapshot:
        start_time = time.time()
        
        context = QualityExecutionContext(
            parent_snapshot=parent_snapshot,
            config=self._config
        )
        
        # Execute independent evaluations followed by normalization
        await self._pipeline.execute(context)
        
        symbol_results = []
        for symbol_key, sym_ctx in context.symbol_contexts.items():
            if not all([
                sym_ctx.strength_result, 
                sym_ctx.consistency_result, 
                sym_ctx.pullback_result, 
                sym_ctx.persistence_result,
                sym_ctx.normalized_metrics
            ]):
                raise IncompleteQualityEvaluationError(f"Missing evaluation metrics for symbol {symbol_key}.")
                
            s_res = cast(TrendStrengthResult, sym_ctx.strength_result)
            c_res = cast(TrendConsistencyResult, sym_ctx.consistency_result)
            pb_res = cast(PullbackQualityResult, sym_ctx.pullback_result)
            p_res = cast(TrendPersistenceResult, sym_ctx.persistence_result)
            n_res = cast(NormalizedQualityMetrics, sym_ctx.normalized_metrics)
            
            res = TrendQualitySymbolResult(
                symbol_key=symbol_key,
                strength_metrics=s_res,
                consistency_metrics=c_res,
                pullback_metrics=pb_res,
                persistence_metrics=p_res,
                normalized_metrics=n_res
            )
            symbol_results.append(res)
            
        duration_ms = (time.time() - start_time) * 1000.0
        
        metadata = TrendQualityMetadata(
            pipeline_version="1.0.0",
            configuration_hash=self._generate_config_hash(),
            configuration_version=self._config.configuration_version,
            quality_algorithm_version=self._config.quality_algorithm_version,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
            evaluation_duration_ms=round(duration_ms, 2)
        )
        
        snapshot = TrendQualitySnapshot(
            quality_snapshot_id=str(uuid.uuid4()),
            source_trend_snapshot_id=parent_snapshot.snapshot_id,
            symbols=symbol_results,
            metadata=metadata
        )
        
        await self._repository.save_quality_snapshot(snapshot)
        return snapshot
