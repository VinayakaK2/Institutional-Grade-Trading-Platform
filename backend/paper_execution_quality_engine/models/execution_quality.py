from pydantic import BaseModel, StrictFloat, ConfigDict

class MarketImpactMetrics(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    expected_execution_price: StrictFloat
    market_impact: StrictFloat
    impact_percentage: StrictFloat
    impact_cost: StrictFloat

class SlippageMetrics(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    expected_price: StrictFloat
    actual_fill_price: StrictFloat
    slippage_amount: StrictFloat
    slippage_percentage: StrictFloat

class SpreadMetrics(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    bid_price: StrictFloat
    ask_price: StrictFloat
    mid_price: StrictFloat
    effective_spread: StrictFloat
    paid_spread: StrictFloat

class GapMetrics(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    gap_up: bool
    gap_down: bool
    gap_size: StrictFloat
    gap_impact: StrictFloat

class LiquidityMetrics(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    available_liquidity: StrictFloat
    executed_quantity: StrictFloat
    remaining_liquidity: StrictFloat
    liquidity_utilization: StrictFloat

class ExecutionQualityReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    market_impact: MarketImpactMetrics
    slippage: SlippageMetrics
    spread_cost: SpreadMetrics
    gap_cost: GapMetrics
    liquidity_metrics: LiquidityMetrics
