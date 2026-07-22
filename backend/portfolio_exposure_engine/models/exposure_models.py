from typing import Dict
from pydantic import BaseModel, Field

class CapitalExposure(BaseModel):
    """Immutable model representing capital measurements."""
    total_invested_capital: float = 0.0
    available_capital: float = 0.0
    capital_utilization_percent: float = 0.0
    cash_allocation: float = 0.0
    
    model_config = {"frozen": True}

class PositionExposure(BaseModel):
    """Immutable model representing individual position measurements."""
    individual_weights: Dict[str, float] = Field(default_factory=dict)
    largest_position: str = ""
    smallest_position: str = ""
    average_position_weight: float = 0.0
    
    model_config = {"frozen": True}

class SectorExposure(BaseModel):
    """Immutable model representing sector exposure measurements."""
    exposure_per_sector: Dict[str, float] = Field(default_factory=dict)
    sector_weights: Dict[str, float] = Field(default_factory=dict)
    sector_distribution: Dict[str, float] = Field(default_factory=dict)
    
    model_config = {"frozen": True}

class IndustryExposure(BaseModel):
    """Immutable model representing industry exposure measurements."""
    exposure_per_industry: Dict[str, float] = Field(default_factory=dict)
    industry_weights: Dict[str, float] = Field(default_factory=dict)
    industry_distribution: Dict[str, float] = Field(default_factory=dict)
    
    model_config = {"frozen": True}

class GrossNetExposure(BaseModel):
    """Immutable model representing aggregate gross and net measurements."""
    gross_exposure: float = 0.0
    net_exposure: float = 0.0
    long_exposure: float = 0.0
    short_exposure: float = 0.0
    
    model_config = {"frozen": True}

class PortfolioExposureMetrics(BaseModel):
    """Immutable model representing high-level exposure counts and metrics."""
    total_positions: int = 0
    sector_count: int = 0
    industry_count: int = 0
    largest_sector_weight: float = 0.0
    largest_position_weight: float = 0.0
    average_position_weight: float = 0.0
    
    model_config = {"frozen": True}

class PortfolioExposureAnalysis(BaseModel):
    """
    A strongly-typed sub-model aggregating all the exposure sub-models.
    """
    capital_exposure: CapitalExposure = Field(default_factory=CapitalExposure)
    position_exposure: PositionExposure = Field(default_factory=PositionExposure)
    sector_exposure: SectorExposure = Field(default_factory=SectorExposure)
    industry_exposure: IndustryExposure = Field(default_factory=IndustryExposure)
    gross_net_exposure: GrossNetExposure = Field(default_factory=GrossNetExposure)
    exposure_metrics: PortfolioExposureMetrics = Field(default_factory=PortfolioExposureMetrics)
    
    model_config = {"frozen": True}
