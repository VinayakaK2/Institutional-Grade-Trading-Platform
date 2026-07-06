from typing import AsyncGenerator
from backend.indicator_engine.contracts.engine import IndicatorQueryEngineContract
from backend.indicator_engine.contracts.repository import IndicatorRepositoryContract
from backend.indicator_engine.models.indicator import IndicatorResult, IndicatorQueryFilters

class IndicatorQueryEngine(IndicatorQueryEngineContract):
    """
    Retrieves calculated indicators from the repository.
    """
    
    def __init__(self, repository: IndicatorRepositoryContract):
        self._repository = repository
        
    def query(self, filters: IndicatorQueryFilters) -> AsyncGenerator[IndicatorResult, None]:
        """
        Retrieves a stream of indicators matching the criteria.
        """
        return self._repository.get_stream(filters)
