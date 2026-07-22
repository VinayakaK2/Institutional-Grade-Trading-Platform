from typing import Dict
from pydantic import BaseModel, Field
from backend.portfolio_state_engine.models.snapshot import PortfolioStateSnapshot
from backend.portfolio_engine.models.configuration import PortfolioConfiguration
from backend.portfolio_exposure_engine.models.exposure_models import PortfolioExposureAnalysis

class PortfolioExposureExecutionContext(BaseModel):
    """
    The immutable external API context. Contains the PortfolioStateSnapshot 
    and necessary configuration.
    """
    portfolio_state_snapshot: PortfolioStateSnapshot
    configuration: PortfolioConfiguration
    
    model_config = {"frozen": True}

class PortfolioExposurePipelineContext(BaseModel):
    """
    Internal context wrapping the execution context. 
    Strictly write-only internally, must never leak outside the pipeline.
    """
    execution_context: PortfolioExposureExecutionContext
    execution_id: str
    exposure_analysis: PortfolioExposureAnalysis = Field(default_factory=PortfolioExposureAnalysis)
    stage_timings: Dict[str, float] = Field(default_factory=dict)
    
    model_config = {"frozen": True}
