from typing import Optional
from backend.trade_validation_engine.signal_aggregation.contracts.repository import ISignalAggregationRepository
from backend.trade_validation_engine.signal_aggregation.models.models import SignalAggregationSnapshot

class PostgreSQLSignalAggregationRepository(ISignalAggregationRepository):
    """
    PostgreSQL stub for Signal Aggregation Repository.
    """
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    async def save(self, snapshot: SignalAggregationSnapshot) -> None:
        pass

    async def get_by_id(self, aggregation_id: str) -> Optional[SignalAggregationSnapshot]:
        return None
        
    async def exists(self, aggregation_id: str) -> bool:
        return False
