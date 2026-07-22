from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field

class CorrelationResult(BaseModel):
    """Base immutable model for correlation outputs."""
    correlation_score: float = 0.0
    confidence: float = 0.0
    calculation_version: str = "1.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"frozen": True}

class PairwiseCorrelation(BaseModel):
    """Immutable representation of a correlation between two entities."""
    left_symbol: str
    right_symbol: str
    correlation: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"frozen": True}

class SymbolCorrelation(CorrelationResult):
    """Pairwise symbol correlations."""
    candidate_to_portfolio_avg: float = 0.0
    candidate_to_portfolio_max: float = 0.0
    candidate_to_portfolio_min: float = 0.0
    pairwise_correlations: Tuple[PairwiseCorrelation, ...] = Field(default_factory=tuple)
    
    model_config = {"frozen": True}

class SectorCorrelation(CorrelationResult):
    """Sector correlation analysis."""
    candidate_sector_to_portfolio_correlation: float = 0.0
    sector_concentration: float = 0.0
    sector_relationships: Tuple[PairwiseCorrelation, ...] = Field(default_factory=tuple)
    
    model_config = {"frozen": True}

class IndustryCorrelation(CorrelationResult):
    """Industry correlation analysis."""
    candidate_industry_to_portfolio_correlation: float = 0.0
    industry_concentration: float = 0.0
    industry_relationships: Tuple[PairwiseCorrelation, ...] = Field(default_factory=tuple)
    
    model_config = {"frozen": True}

class StrategyCorrelation(CorrelationResult):
    """Strategy correlation analysis."""
    strategy_overlap: float = 0.0
    strategy_diversification: float = 0.0
    strategy_concentration: float = 0.0
    
    model_config = {"frozen": True}

class DirectionalCorrelation(CorrelationResult):
    """Directional correlation analysis."""
    long_exposure_correlation: float = 0.0
    short_exposure_correlation: float = 0.0
    net_directional_concentration: float = 0.0
    
    model_config = {"frozen": True}

class PortfolioCorrelationAnalysis(BaseModel):
    """Aggregates all raw correlation sub-models."""
    symbol_correlation: SymbolCorrelation = Field(default_factory=SymbolCorrelation)
    sector_correlation: SectorCorrelation = Field(default_factory=SectorCorrelation)
    industry_correlation: IndustryCorrelation = Field(default_factory=IndustryCorrelation)
    strategy_correlation: StrategyCorrelation = Field(default_factory=StrategyCorrelation)
    directional_correlation: DirectionalCorrelation = Field(default_factory=DirectionalCorrelation)
    
    model_config = {"frozen": True}

class CorrelationMetrics(BaseModel):
    """Aggregates derived metrics representing portfolio characteristics."""
    average_correlation: float = 0.0
    maximum_correlation: float = 0.0
    correlation_distribution: Dict[str, float] = Field(default_factory=dict)
    diversification_score: float = 0.0
    concentration_score: float = 0.0
    
    model_config = {"frozen": True}
