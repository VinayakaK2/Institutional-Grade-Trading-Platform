from typing import List, Dict
from pydantic import BaseModel
import random

from backend.watchlist_engine.models.models import WatchlistSymbol
from backend.market_data.models.symbol import SymbolReference, ExchangeReference
from backend.trend_engine.models.models import TrendDirection, TrendState

# Assume quality models are standard (TrendLifecycleState etc are generated based on deterministic inputs)
from backend.trend_engine.lifecycle.models.models import TrendLifecycleState

class DeterministicDataset(BaseModel):
    """A generated dataset containing symbols and their mathematically expected outcomes."""
    symbols: List[WatchlistSymbol]
    
    # Expected outcomes indexed by symbol key "SYMBOL:EXCHANGE"
    expected_directions: Dict[str, TrendDirection]
    expected_states: Dict[str, TrendState]
    expected_lifecycles: Dict[str, TrendLifecycleState]
    expected_normalized_strengths: Dict[str, float]
    
    # Mocks or simulated provider data corresponding to each symbol
    # For Phase 7.1-7.5, we just provide the symbol and expect the Certification mocks to handle data routing
    # OR we provide the raw indicator values here to feed into providers.
    simulated_emas: Dict[str, Dict[str, float]]
    simulated_structures: Dict[str, str]

class DeterministicDatasetGenerator:
    """Generates explicit Trend datasets and their exact mathematically expected outputs."""
    
    def __init__(self, seed: int = 42):
        self._seed = seed
        random.seed(self._seed)
        
    def generate(self, count: int) -> DeterministicDataset:
        symbols = []
        expected_directions = {}
        expected_states = {}
        expected_lifecycles = {}
        expected_normalized_strengths = {}
        simulated_emas = {}
        simulated_structures = {}
        
        # We rotate through deterministic scenarios
        # 0: Strong Uptrend, 1: Weak Downtrend, 2: Sideways, 3: Reversal, 4: Flat
        
        for i in range(count):
            sym = f"SYM{i}"
            exc = "TEST"
            key = f"{sym}:{exc}"
            
            w_sym = WatchlistSymbol(
                symbol=SymbolReference(symbol=sym, exchange=ExchangeReference(code=exc))
            )
            symbols.append(w_sym)
            
            scenario = i % 5
            
            if scenario == 0:
                # Strong Uptrend (EMA20 > EMA50 > EMA200)
                expected_directions[key] = TrendDirection.UPTREND
                expected_states[key] = TrendState.VALID
                expected_lifecycles[key] = TrendLifecycleState.ACTIVE
                expected_normalized_strengths[key] = 0.95
                simulated_emas[key] = {"ema_20": 100.0, "ema_50": 90.0, "ema_200": 80.0}
                simulated_structures[key] = "HH_HL"
            elif scenario == 1:
                # Strong Downtrend
                expected_directions[key] = TrendDirection.DOWNTREND
                expected_states[key] = TrendState.VALID
                expected_lifecycles[key] = TrendLifecycleState.ACTIVE
                expected_normalized_strengths[key] = 0.85
                simulated_emas[key] = {"ema_20": 80.0, "ema_50": 90.0, "ema_200": 100.0}
                simulated_structures[key] = "LH_LL"
            elif scenario == 2:
                # Sideways (Choppy EMAs)
                expected_directions[key] = TrendDirection.SIDEWAYS
                expected_states[key] = TrendState.INVALID
                expected_lifecycles[key] = TrendLifecycleState.ENDED
                expected_normalized_strengths[key] = 0.0
                simulated_emas[key] = {"ema_20": 95.0, "ema_50": 96.0, "ema_200": 94.0}
                simulated_structures[key] = "CHOPPY"
            elif scenario == 3:
                # Reversal (EMA 20 crossed 50 recently)
                expected_directions[key] = TrendDirection.UPTREND
                expected_states[key] = TrendState.INCOMPLETE
                expected_lifecycles[key] = TrendLifecycleState.WEAKENING
                expected_normalized_strengths[key] = 0.4
                simulated_emas[key] = {"ema_20": 91.0, "ema_50": 90.0, "ema_200": 95.0}
                simulated_structures[key] = "HH_HL"
            else:
                # Flat Market
                expected_directions[key] = TrendDirection.UNKNOWN
                expected_states[key] = TrendState.INVALID
                expected_lifecycles[key] = TrendLifecycleState.ENDED
                expected_normalized_strengths[key] = 0.0
                simulated_emas[key] = {"ema_20": 100.0, "ema_50": 100.0, "ema_200": 100.0}
                simulated_structures[key] = "FLAT"
                
        return DeterministicDataset(
            symbols=symbols,
            expected_directions=expected_directions,
            expected_states=expected_states,
            expected_lifecycles=expected_lifecycles,
            expected_normalized_strengths=expected_normalized_strengths,
            simulated_emas=simulated_emas,
            simulated_structures=simulated_structures
        )
