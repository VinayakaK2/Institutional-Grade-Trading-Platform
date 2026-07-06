import pytest
from backend.historical_data.models.raw import RawCandle
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.market_data.models.timeframe import Timeframe
from backend.data_validation.cleaning.engine import CleaningEngine
from backend.data_validation.cleaning.rules.basic import DuplicateRemovalRule, WhitespaceCleanupRule
from backend.data_validation.models.report import ValidationReport, ValidationResult

@pytest.fixture
def sample_report():
    report = ValidationReport()
    report.structural_findings.errors.append(
        ValidationResult(
            rule_name="Structural",
            is_valid=False,
            record_timestamp="2024-01-02",
            message="Error"
        )
    )
    return report

@pytest.mark.asyncio
async def test_cleaning_engine_removes_invalid_and_cleans(sample_report):
    engine = CleaningEngine([DuplicateRemovalRule(), WhitespaceCleanupRule()])
    sym = SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))
    tf = Timeframe.D1
    
    records = [
        RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-01 ", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=10), # Valid, needs whitespace clean
        RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-02", raw_open=None, raw_high=2, raw_low=1, raw_close=2, raw_volume=10), # Invalid from report
        RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-03", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=10), # Valid
        RawCandle(provider="t", symbol=sym, timeframe=tf, raw_timestamp="2024-01-03", raw_open=1, raw_high=2, raw_low=1, raw_close=2, raw_volume=10), # Duplicate
    ]
    
    result = await engine.run(records, sample_report)
    
    assert len(result.cleaned_records) == 2
    assert result.cleaned_records[0].raw_timestamp == "2024-01-01" # Whitespace removed
    assert result.cleaned_records[1].raw_timestamp == "2024-01-03" # Duplicate removed
    
    assert len(result.rejected_records) == 2
    rejected_timestamps = [r.raw_timestamp for r in result.rejected_records]
    assert "2024-01-02" in rejected_timestamps
    assert "2024-01-03" in rejected_timestamps # The duplicate
