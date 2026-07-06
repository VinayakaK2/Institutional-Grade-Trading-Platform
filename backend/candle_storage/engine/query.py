"""
Candle Query Engine
Orchestrates reads, explicitly enforcing dataset isolation.
"""
from typing import AsyncGenerator, Any
import logging

from backend.candle_storage.contracts.engine import CandleQueryEngineContract
from backend.candle_storage.contracts.repository import CandleRepositoryContract
from backend.candle_storage.models.dataset import CandleQueryFilters
from backend.candle_storage.exceptions import CandleQueryException

logger = logging.getLogger(__name__)

class CandleQueryEngine(CandleQueryEngineContract):
    """
    Implements query logic, ensuring dataset type is explicitly provided 
    and enforcing validations on dataset selection before passing to the repository.
    """
    def __init__(self, repository: CandleRepositoryContract):
        self._repository = repository
        
    async def query(self, filters: CandleQueryFilters) -> AsyncGenerator[Any, None]:
        """
        Executes a query based on the explicit filters.
        Ensures strict boundary checks.
        """
        # Validate dataset requirements directly (models handle this in init, but we enforce explicitly here too)
        try:
            filters.validate_dataset_requirements()
        except ValueError as e:
            raise CandleQueryException(f"Invalid query filters: {e}")
            
        logger.debug(f"Executing Candle Query: Dataset={filters.dataset_type.value}, Symbol={filters.symbol.symbol}, Timeframe={filters.timeframe.value}")
        
        async for candle in self._repository.get_stream(filters):
            yield candle
