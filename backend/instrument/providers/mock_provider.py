"""
Mock Provider for testing and local development
"""
import asyncio
from typing import List, AsyncGenerator
from backend.instrument.providers.base import BaseSymbolProvider
from backend.instrument.models.instrument import Instrument
from backend.instrument.models.exchange import ExchangeMetadata

class MockSymbolProvider(BaseSymbolProvider):
    """
    In-memory provider for testing without external network calls.
    """
    def __init__(self, name: str = "mock_provider"):
        super().__init__(name)
        self.exchanges: List[ExchangeMetadata] = []
        self.instruments: List[Instrument] = []
        self.simulate_delay: float = 0.0

    async def fetch_exchanges(self) -> List[ExchangeMetadata]:
        if self.simulate_delay > 0:
            await asyncio.sleep(self.simulate_delay)
        return self.exchanges
        
    async def fetch_all_instruments(self) -> AsyncGenerator[List[Instrument], None]:
        if self.simulate_delay > 0:
            await asyncio.sleep(self.simulate_delay)
        
        # Yield in batches of 10
        batch_size = 10
        for i in range(0, len(self.instruments), batch_size):
            yield self.instruments[i:i + batch_size]
            
    async def fetch_updates_since(self, version_id: str) -> AsyncGenerator[List[Instrument], None]:
        # For mock, we just yield all as updates.
        async for batch in self.fetch_all_instruments():
            yield batch
