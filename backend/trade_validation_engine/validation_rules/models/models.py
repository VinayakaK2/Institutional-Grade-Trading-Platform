from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

from backend.trade_validation_engine.validation_rules.config.config import ValidationRulesConfig

class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCOMPLETE = "INCOMPLETE"

class ValidationContext(BaseModel):
    """
    Immutable context passed through the validation rules pipeline.
    Contains strictly reference identifiers and configuration.
    """
    symbol: str = Field(description="Target symbol")
    timeframe: str = Field(description="Target timeframe")
    dataset_version: int = Field(description="Dataset version")
    
    aggregated_trade_snapshot_version: str = Field(description="ID of the AggregatedTradeEvidence snapshot")
    
    configuration: ValidationRulesConfig = Field(description="Pipeline configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata related to the validation run")
    
    model_config = {"frozen": True}

class ValidationEvidence(BaseModel):
    """
    Evidence model capturing explicit values verified by a rule.
    """
    verified_properties: Dict[str, Any] = Field(description="The exact properties verified by this rule")
    expected_values: Dict[str, Any] = Field(default_factory=dict, description="The expected values (if applicable)")
    
    model_config = {"frozen": True}

class RuleValidationResult(BaseModel):
    """
    Structured outcome of a single rule execution.
    """
    rule_id: str = Field(description="Unique identifier for the rule")
    rule_version: str = Field(description="Version of the executed rule")
    status: str = Field(description="Outcome status: PASS, FAIL, or SKIP")
    reason: Optional[str] = Field(default=None, description="Explanation for FAIL or SKIP")
    validation_evidence: Optional[ValidationEvidence] = Field(default=None, description="Explicit verification details")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Rule-specific diagnostic metadata")
    
    model_config = {"frozen": True}

class ValidationReportSummary(BaseModel):
    """
    High-level summary of the pipeline execution.
    """
    total_rules_executed: int = Field(description="Number of rules that ran")
    passed_rules: int = Field(description="Number of rules that passed")
    failed_rules: int = Field(description="Number of rules that failed")
    skipped_rules: int = Field(description="Number of rules that were skipped")
    total_duration_ms: int = Field(description="Total time taken by the pipeline in ms")
    
    model_config = {"frozen": True}

class ValidationReport(BaseModel):
    """
    Immutable root aggregate for the entire Validation Rules phase.
    """
    validation_id: str = Field(description="Deterministic ID for this report")
    symbol: str = Field(description="Target symbol")
    timeframe: str = Field(description="Target timeframe")
    dataset_version: int = Field(description="Dataset version")
    
    configuration_hash: str = Field(description="Hash of the ValidationRulesConfig")
    validation_pipeline_version: str = Field(description="Version of the pipeline configuration")
    
    status: ValidationStatus = Field(description="Overall validation status: PASS, FAIL, or INCOMPLETE")
    
    rule_results: List[RuleValidationResult] = Field(description="Detailed results from each rule")
    summary: ValidationReportSummary = Field(description="Execution summary metrics")
    
    created_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Time of report creation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Root metadata")
    
    model_config = {"frozen": True}
