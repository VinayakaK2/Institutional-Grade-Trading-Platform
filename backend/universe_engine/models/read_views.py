"""
Read Models for Universe Queries.
Provides decoupled, projection-based views of the universe specifically
tailored for downstream consumers like Candidate Selection.
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

from backend.market_data.models.symbol import SymbolReference


class CandidateUniverseSymbol(BaseModel):
    """
    Projected view of a symbol specifically tailored for the Watchlist Candidate Selection phase.
    Strips away all internal classification logic, leaving only the essential filtering flags.
    """
    model_config = ConfigDict(frozen=True)

    symbol: SymbolReference
    exchange: str
    instrument_type: str
    is_active: bool
    is_certified: bool


class CandidateUniverseView(BaseModel):
    """
    Projected view of a Universe Snapshot designed for consumption by downstream phases.
    Contains only the data required to build a candidate watchlist.
    """
    model_config = ConfigDict(frozen=True)

    universe_snapshot_id: str
    universe_version: int
    pipeline_version: str
    created_at: datetime
    symbols: List[CandidateUniverseSymbol]
