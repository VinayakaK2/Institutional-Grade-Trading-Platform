from abc import ABC, abstractmethod
from typing import List
from backend.universe_engine.models.universe import UniverseInstrument

class IUniverseProvider(ABC):
    """
    Contract for retrieving the raw universe of instruments from an external provider.

    PROVIDER MAPPING CONTRACT:
    ───────────────────────────
    1. The provider is strictly responsible for fetching raw exchange data and mapping it
       into the standard `UniverseInstrument` model.
    2. The filtering pipeline must NEVER interpret raw provider payloads directly.
    3. Core attributes (instrument_type, trading_status, market_segment, is_delisted)
       must be parsed into their respective strong-typed Enums.
    4. Any unparseable or unrecognized values must be mapped to the `UNKNOWN` enum
       member rather than raising an exception during parsing.
    5. All other provider-specific fields (e.g., 'series', 'board', 'tick_size')
       must be dumped into `UniverseInstrument.provider_attributes` and MUST NOT
       be relied upon by the core business logic.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def fetch_universe(self) -> List[UniverseInstrument]:
        pass
