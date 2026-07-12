from pydantic import BaseModel, ConfigDict
from backend.liquidity_grab_engine.detection.models.models import LiquidityGrabCandidate
from backend.liquidity_grab_engine.quality.models.models import LiquidityGrabQualityReport
from backend.liquidity_grab_engine.detection.contracts.market_data import ICandleSeries
from backend.liquidity_grab_engine.config.config import LiquidityGrabConfiguration

class LiquidityGrabLifecycleContext(BaseModel):
    """
    Context required for evaluating a Liquidity Grab Lifecycle.
    Contains evaluation candle series (candles strictly after detection).
    """
    candidate: LiquidityGrabCandidate
    quality_report: LiquidityGrabQualityReport
    evaluation_candles: ICandleSeries
    dataset_version: int
    configuration: LiquidityGrabConfiguration
    
    class Metadata(BaseModel):
        pipeline_version: str
        model_config = ConfigDict(frozen=True)
        
    metadata: Metadata

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)
