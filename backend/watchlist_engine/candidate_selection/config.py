from pydantic import BaseModel, Field
from typing import List


class CandidateSelectionSettings(BaseModel):
    """
    Configuration settings for the Candidate Selection Engine.
    """
    candidate_limit: int = Field(default=500, description="Maximum number of candidates to select for the daily watchlist.")
    default_ordering: str = Field(default="symbol_name", description="The default ordering strategy. Only 'symbol_name' is supported currently.")
    always_include: List[str] = Field(default_factory=list, description="List of tickers to always include, bypassing filters.")
    always_exclude: List[str] = Field(default_factory=list, description="List of tickers to completely exclude.")
