from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Optional
from datetime import datetime

class UniverseOptimizationConfiguration(BaseModel):
    """
    Configuration for the optimization engine.
    """
    enable_incremental: bool = True
    enable_batching: bool = True
    enable_parallel: bool = True
    batch_size: int = 500
    max_workers: int = 4

class OptimizationMetrics(BaseModel):
    """
    Metrics captured during the optimization process.
    """
    total_symbols: int = 0
    symbols_reused: int = 0
    symbols_reprocessed: int = 0
    batch_count: int = 0
    parallel_workers_used: int = 0
    processing_time_ms: float = 0.0

class UniverseOptimizationContext(BaseModel):
    """
    Mutable context used during the optimization pipeline execution.
    """
    run_id: str
    parent_classified_universe_id: str
    previous_optimized_universe_id: Optional[str] = None
    config: UniverseOptimizationConfiguration
    
    # Internal working state (lazy evaluation makes lists unnecessary if streaming,
    # but for simple context passing we can store counts here).
    # Memory management dictates we avoid duplicating large objects in memory.
    metrics: OptimizationMetrics = Field(default_factory=OptimizationMetrics)
    started_at: datetime
    
class OptimizedUniverse(BaseModel):
    """
    Immutable resulting artifact of the Optimization Engine.
    
    Contains NO duplicated business objects. All business data is read from the
    parent_classified_universe_id. This snapshot stores optimization execution metadata.
    """
    model_config = ConfigDict(frozen=True)

    optimized_universe_id: str
    parent_classified_universe_id: str
    previous_optimized_universe_id: Optional[str]
    pipeline_version: str
    config_hash: str
    created_at: datetime
    
    configuration_snapshot: UniverseOptimizationConfiguration
    optimization_metrics: OptimizationMetrics
    
    # Store fingerprints for incremental diff detection in future runs
    symbol_fingerprints: Dict[str, str] = Field(default_factory=dict)

class UniverseOptimizationResult(BaseModel):
    """
    Wrapper for the output of the Optimization Engine.
    """
    model_config = ConfigDict(frozen=True)
    universe: OptimizedUniverse
