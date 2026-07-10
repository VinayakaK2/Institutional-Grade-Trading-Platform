from backend.trend_engine.certification.dataset.generator import DeterministicDatasetGenerator
from backend.trend_engine.models.models import TrendDirection
from backend.trend_engine.lifecycle.models.models import TrendLifecycleState

def test_dataset_generator_determinism():
    gen1 = DeterministicDatasetGenerator(seed=42)
    ds1 = gen1.generate(100)
    
    gen2 = DeterministicDatasetGenerator(seed=42)
    ds2 = gen2.generate(100)
    
    assert len(ds1.symbols) == 100
    assert len(ds2.symbols) == 100
    
    # Verify outputs are identical for the same seed
    for i in range(100):
        key1 = f"{ds1.symbols[i].symbol.symbol}:{ds1.symbols[i].symbol.exchange.code}"
        key2 = f"{ds2.symbols[i].symbol.symbol}:{ds2.symbols[i].symbol.exchange.code}"
        
        assert key1 == key2
        assert ds1.expected_directions[key1] == ds2.expected_directions[key2]
        assert ds1.expected_states[key1] == ds2.expected_states[key2]
        assert ds1.expected_lifecycles[key1] == ds2.expected_lifecycles[key2]
        assert ds1.expected_normalized_strengths[key1] == ds2.expected_normalized_strengths[key2]
        
def test_dataset_generator_scenarios():
    gen = DeterministicDatasetGenerator(seed=42)
    ds = gen.generate(5)
    
    # 0: Uptrend
    k0 = f"{ds.symbols[0].symbol.symbol}:{ds.symbols[0].symbol.exchange.code}"
    assert ds.expected_directions[k0] == TrendDirection.UPTREND
    
    # 1: Downtrend
    k1 = f"{ds.symbols[1].symbol.symbol}:{ds.symbols[1].symbol.exchange.code}"
    assert ds.expected_directions[k1] == TrendDirection.DOWNTREND
    
    # 2: Sideways
    k2 = f"{ds.symbols[2].symbol.symbol}:{ds.symbols[2].symbol.exchange.code}"
    assert ds.expected_directions[k2] == TrendDirection.SIDEWAYS
    
    # 3: Reversal (Uptrend)
    k3 = f"{ds.symbols[3].symbol.symbol}:{ds.symbols[3].symbol.exchange.code}"
    assert ds.expected_directions[k3] == TrendDirection.UPTREND
    assert ds.expected_lifecycles[k3] == TrendLifecycleState.WEAKENING
    
    # 4: Flat
    k4 = f"{ds.symbols[4].symbol.symbol}:{ds.symbols[4].symbol.exchange.code}"
    assert ds.expected_directions[k4] == TrendDirection.UNKNOWN
