import pytest
from datetime import datetime, timezone
from backend.watchlist_engine.candidate_selection.config import CandidateSelectionSettings
from backend.watchlist_engine.candidate_selection.stages import ManualIncludeStage, CandidateSelectionStage, ManualExcludeStage
from backend.watchlist_engine.models.models import WatchlistExecutionContext, WatchlistCandidate, WatchlistSymbol, WatchlistStageStatus
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.watchlist_engine.models.exceptions import WatchlistValidationError

def make_candidate(symbol: str, is_active: bool = True, is_certified: bool = True) -> WatchlistCandidate:
    return WatchlistCandidate(
        watchlist_symbol=WatchlistSymbol(
            symbol=SymbolReference(symbol=symbol, exchange=ExchangeReference(code="NASDAQ")),
            market_segment="EQUITY",
            instrument_type="EQUITY"
        ),
        stage_metadata={
            "is_active": is_active,
            "is_certified": is_certified
        }
    )

@pytest.mark.asyncio
async def test_manual_include_stage_success() -> None:
    settings = CandidateSelectionSettings(always_include=["AAPL"])
    stage = ManualIncludeStage(settings)
    
    context = WatchlistExecutionContext(
        run_id="r1",
        snapshot_id="s1",
        started_at=datetime.now(timezone.utc),
        candidates=[make_candidate("AAPL"), make_candidate("MSFT")],
    )
    
    result = await stage.execute(context)
    
    assert result.status == WatchlistStageStatus.SUCCESS
    assert context.candidates[0].stage_metadata["is_manual_include"] is True
    assert context.candidates[1].stage_metadata["is_manual_include"] is False

@pytest.mark.asyncio
async def test_manual_include_stage_raises_validation_error() -> None:
    settings = CandidateSelectionSettings(always_include=["TSLA"])
    stage = ManualIncludeStage(settings)
    
    context = WatchlistExecutionContext(
        run_id="r1",
        snapshot_id="s1",
        started_at=datetime.now(timezone.utc),
        candidates=[make_candidate("AAPL")],
    )
    
    with pytest.raises(WatchlistValidationError):
        await stage.execute(context)

@pytest.mark.asyncio
async def test_candidate_selection_stage() -> None:
    settings = CandidateSelectionSettings(candidate_limit=2)
    stage = CandidateSelectionStage(settings)
    
    context = WatchlistExecutionContext(
        run_id="r1",
        snapshot_id="s1",
        started_at=datetime.now(timezone.utc),
        candidates=[
            make_candidate("Z", True, True),
            make_candidate("A", True, True),
            make_candidate("B", True, True),
            make_candidate("C", False, True),  # inactive
            make_candidate("D", True, False),  # uncertified
        ],
    )
    
    # mark Z as manual include manually to test prioritization
    context.candidates[0].stage_metadata["is_manual_include"] = True
    
    result = await stage.execute(context)
    
    assert result.status == WatchlistStageStatus.SUCCESS
    assert len(context.candidates) == 2
    
    # "A" should be selected because it's first alphabetically among regular, and Z is manual include.
    # Manual includes bypass alphabetical priority for selection, but final is sorted alphabetically.
    symbols = [c.watchlist_symbol.symbol.symbol for c in context.candidates]
    assert symbols == ["A", "Z"]

@pytest.mark.asyncio
async def test_manual_exclude_stage() -> None:
    settings = CandidateSelectionSettings(always_exclude=["MSFT"])
    stage = ManualExcludeStage(settings)
    
    context = WatchlistExecutionContext(
        run_id="r1",
        snapshot_id="s1",
        started_at=datetime.now(timezone.utc),
        candidates=[make_candidate("AAPL"), make_candidate("MSFT")],
    )
    
    result = await stage.execute(context)
    
    assert result.status == WatchlistStageStatus.SUCCESS
    assert len(context.candidates) == 1
    assert context.candidates[0].watchlist_symbol.symbol.symbol == "AAPL"
