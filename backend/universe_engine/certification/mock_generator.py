import random
from typing import List
from backend.market_data.models.symbol import SymbolReference, ExchangeReference

class DeterministicMockDatasetGenerator:
    """
    Internal generator that creates deterministic datasets for stress testing 
    and regression testing. It uses a fixed seed to guarantee identical outputs.
    
    DETERMINISTIC DATASET CONTRACT:
    - Random Seed: Fixed at 42 by default to guarantee reproducibility.
    - Dataset Generation Rules: 
      - Always generates exactly the requested number of `SymbolReference` items.
      - Uses a predictable random sequence mapped to a predefined list of exchanges.
    - Symbol Generation Rules:
      - Tickers are sequentially generated (`TICK0`, `TICK1`, etc.).
      - Exchanges are randomly (but deterministically) assigned from `_exchanges`.
    - Edge-Case Generation Rules:
      - Contains explicit duplicate symbols for uniqueness validation.
      - Contains explicitly invalid/unrecognized exchanges to verify filter handling.
      - Must never be modified in ways that alter historical dataset shapes or sequences, 
        as this would invalidate existing regression tests.
    """
    
    def __init__(self, seed: int = 42):
        self._seed = seed
        # We instantiate a new Random object so we don't interfere with the global random state
        self._rng = random.Random(seed) # nosec
        
        self._sectors = ["Technology", "Healthcare", "Financials", "Energy", "Consumer Discretionary"]
        self._industries = ["Software", "Biotech", "Banks", "Oil", "Retail", "Semiconductors"]
        self._exchanges = ["NYSE", "NASDAQ", "ARCA", "BATS", "IEX"]
        
    def generate_symbols(self, count: int) -> List[SymbolReference]:
        """Generates a base dataset of a given size."""
        symbols = []
        for i in range(count):
            ticker = f"TICK{i}"
            exchange = self._rng.choice(self._exchanges)
                
            ex_ref = ExchangeReference(
                code=exchange
            )
            
            sym_ref = SymbolReference(
                symbol=ticker,
                exchange=ex_ref
            )
            symbols.append(sym_ref)
            
        return symbols

    def get_tiny_dataset(self) -> List[SymbolReference]:
        return self.generate_symbols(10)
        
    def get_small_dataset(self) -> List[SymbolReference]:
        return self.generate_symbols(100)
        
    def get_medium_dataset(self) -> List[SymbolReference]:
        return self.generate_symbols(500)
        
    def get_large_dataset(self) -> List[SymbolReference]:
        return self.generate_symbols(1000)

    def get_edge_case_dataset(self) -> List[SymbolReference]:
        """
        Creates a dataset containing explicitly engineered edge cases.
        """
        base = self.generate_symbols(20)
        
        # 1. Duplicate symbol (identical ticker and symbol_id to base[0])
        duplicate = base[0].model_copy(deep=True)
        base.append(duplicate)
        
        # 2. Missing metadata (not applicable for SymbolReference anymore, just unique symbol)
        missing_meta = self.generate_symbols(1)[0].model_copy(update={"symbol": "SYM_MISSING"})
        base.append(missing_meta)
        
        # 3. Unknown sector / industry (not applicable for SymbolReference anymore)
        unknown_class = self.generate_symbols(1)[0].model_copy(update={"symbol": "SYM_UNK"})
        base.append(unknown_class)
        
        # 4. Invalid exchange
        invalid_ex = self.generate_symbols(1)[0].model_copy(deep=True)
        invalid_ex = invalid_ex.model_copy(update={
            "symbol": "SYM_INVEX", 
            "exchange": ExchangeReference(code="INVALID")
        })
        base.append(invalid_ex)
        
        return base
