from datetime import datetime
from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from backend.universe_engine.models.universe import UniverseInstrument


class DataQualityRejectionReason(str, Enum):
    """
    Strongly typed reasons for rejecting an instrument during data quality validation.
    """

    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    TOO_MANY_GAPS = "TOO_MANY_GAPS"
    PROLONGED_SUSPENSION = "PROLONGED_SUSPENSION"
    DATA_CORRUPTED = "DATA_CORRUPTED"
    INCONSISTENT_CORPORATE_ACTIONS = "INCONSISTENT_CORPORATE_ACTIONS"
    MISSING_DATA = "MISSING_DATA"


class DataQualityRejectionDetail(BaseModel):
    """
    Structured record of why an instrument failed data quality validation.
    """

    instrument_symbol: str
    stage_name: str
    reason: DataQualityRejectionReason
    measured_value: str
    threshold: str


class DataQualityFilterConfiguration(BaseModel):
    """
    Configuration parameters for the Data Quality Filter Engine.
    """

    min_history_days: int = Field(
        252, description="Minimum required calendar days of history."
    )
    max_missing_candles_percentage: float = Field(
        0.05,
        description="Maximum allowed percentage of unexpected missing trading sessions.",
    )
    max_consecutive_suspensions: int = Field(
        5,
        description="Maximum allowed consecutive unexpected missing sessions before classifying as a prolonged suspension.",
    )
    check_corporate_actions: bool = Field(
        True, description="Whether to strictly enforce corporate action consistency."
    )


class DataQualityFilterStatistics(BaseModel):
    """
    Strongly typed statistics for the Data Quality Filter execution.
    """

    initial_instrument_count: int = 0
    final_certified_count: int = 0
    history_rejections: int = 0
    gap_rejections: int = 0
    suspension_rejections: int = 0
    completeness_rejections: int = 0
    corporate_action_rejections: int = 0
    missing_data_rejections: int = 0
    processing_time_ms: float = 0.0
    pipeline_version: str = "1.0.0"


class DataQualityFilterContext(BaseModel):
    """
    Mutable context used during the pipeline execution.
    Implements a Fail Fast policy: instruments that fail are removed
    from certified_instruments and appended to rejected_details.
    """

    run_id: str
    parent_snapshot_id: str
    config: DataQualityFilterConfiguration
    certified_instruments: List[UniverseInstrument]
    rejected_details: List[DataQualityRejectionDetail] = Field(default_factory=list)
    statistics: DataQualityFilterStatistics = Field(
        default_factory=DataQualityFilterStatistics
    )
    started_at: datetime
    shared_state: Dict[str, Any] = Field(default_factory=dict)


class CertifiedUniverse(BaseModel):
    """
    Immutable representation of the universe that has passed structural data quality validation.
    
    CERTIFICATION LIFETIME:
    A CertifiedUniverse snapshot represents the dataset quality at a specific point in time. 
    It is NOT indefinitely valid. As historical data is continuously appended, or corporate actions occur,
    subsequent pipeline executions will evaluate the updated dataset and MUST generate a new 
    CertifiedUniverse snapshot to reflect the latest validation state.
    """

    model_config = ConfigDict(frozen=True)

    certified_universe_id: str
    parent_snapshot_id: str
    pipeline_version: str
    config_hash: str
    dataset_version: str

    created_at: datetime

    certified_symbols: List[UniverseInstrument]
    rejected_symbols: List[DataQualityRejectionDetail]

    configuration_snapshot: DataQualityFilterConfiguration
    statistics: DataQualityFilterStatistics
