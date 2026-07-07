"""
Watchlist Certification Engine
==============================

Facade for executing the certification pipeline.
"""
import time
import platform
import psutil
import os
from typing import Optional

from backend.watchlist_engine.certification.models import (
    BusinessMetadata,
    ExecutionMetadata,
    CertificationReport,
    CertificationContext
)
from backend.watchlist_engine.certification.pipeline import CertificationPipeline
from backend.watchlist_engine.certification.stages.functional import FunctionalVerificationStage
from backend.watchlist_engine.certification.stages.regression import RegressionVerificationStage
from backend.watchlist_engine.certification.stages.determinism import DeterminismVerificationStage
from backend.watchlist_engine.certification.stages.stress import StressVerificationStage
from backend.watchlist_engine.certification.mock_generator import MockDatasetGenerator

# Import actual engine dependencies
from backend.watchlist_engine.engine.engine import WatchlistEngine
from backend.watchlist_engine.optimization.engine import WatchlistOptimizationEngine
from backend.watchlist_engine.repository.repository import InMemoryWatchlistRepository
from backend.watchlist_engine.pipeline.pipeline import WatchlistExecutionPipeline
from backend.watchlist_engine.validation.validators import WatchlistValidator
from backend.watchlist_engine.models.config import (
    WatchlistSettings,
    WatchlistValidationSettings,
    WatchlistOptimizationSettings,
    WatchlistPipelineSettings
)


class CertificationEngine:
    """
    Builds and executes the certification pipeline.
    """
    
    def __init__(self) -> None:
        pass
        
    def _create_context(self) -> CertificationContext:
        context = CertificationContext()
        context.dataset_generator = MockDatasetGenerator(seed=42)
        
        # Factory method to build a fully wired up, clean engine stack
        def build_engine(opt_settings: Optional[WatchlistOptimizationSettings] = None) -> WatchlistOptimizationEngine:
            repo = InMemoryWatchlistRepository()
            
            # 1. Base Engine
            settings = WatchlistSettings(
                validation=WatchlistValidationSettings(
                    allow_empty_watchlist=False,
                    max_watchlist_size=2000
                ),
                pipeline=WatchlistPipelineSettings()
            )
            base_pipeline = WatchlistExecutionPipeline(settings=settings.pipeline)
            validator = WatchlistValidator(settings.validation)
            base_engine = WatchlistEngine(
                pipeline=base_pipeline,
                repository=repo,
                settings=settings,
                validator=validator
            )
            
            # (Freshness Engine logic is handled inside WatchlistEngine pipeline if needed, or separate layer. 
            # For certification of optimization layer, we just use the base_engine)
            
            if not opt_settings:
                opt_settings = WatchlistOptimizationSettings()
                
            opt_engine = WatchlistOptimizationEngine(
                inner=base_engine,
                settings=opt_settings,
                repository=repo
            )
            
            return opt_engine
            
        context.build_engine = build_engine
        return context

    async def run_certification(self) -> CertificationReport:
        """
        Executes the full certification pipeline and returns an immutable report.
        """
        start_time = time.time()
        
        pipeline = CertificationPipeline()
        # Enforce execution order
        pipeline.register_stage(FunctionalVerificationStage())
        pipeline.register_stage(RegressionVerificationStage())
        pipeline.register_stage(DeterminismVerificationStage())
        pipeline.register_stage(StressVerificationStage())
        
        context = self._create_context()
        await pipeline.execute(context)
        
        # Build Business Metadata
        biz_metadata = BusinessMetadata(
            pipeline_version="1.0.0",
            config_hash="certified_config",
            business_fingerprint_version=1
        )
        
        # Build Execution Metadata
        process = psutil.Process(os.getpid())
        mem_usage_mb = process.memory_info().rss / (1024 * 1024)
        
        exec_metadata = ExecutionMetadata(
            python_version=platform.python_version(),
            execution_time_ms=(time.time() - start_time) * 1000,
            memory_usage_mb=mem_usage_mb,
            environment_info={
                "os": platform.system(),
                "release": platform.release(),
                "machine": platform.machine()
            }
        )
        
        all_passed = all(stage.passed for stage in context.stage_results)
        
        return CertificationReport(
            passed=all_passed,
            business_metadata=biz_metadata,
            execution_metadata=exec_metadata,
            stage_results=context.stage_results
        )
