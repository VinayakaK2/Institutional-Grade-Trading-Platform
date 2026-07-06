import logging
from typing import List, Dict, Any
from backend.market_data.models.candle import Candle
from backend.indicator_engine.contracts.engine import IndicatorCalculationEngineContract
from backend.indicator_engine.contracts.calculator import IndicatorCalculatorContract
from backend.indicator_engine.models.indicator import IndicatorResult
from backend.indicator_engine.engine.validation import IndicatorValidationEngine

logger = logging.getLogger(__name__)

class IndicatorEngine(IndicatorCalculationEngineContract):
    """
    Core calculation engine that accepts a candle series, 
    routes it to all registered calculators, and returns immutable results.
    """
    
    def __init__(self, calculators: List[IndicatorCalculatorContract]):
        self._calculators = calculators
        
    async def process_batch(self, candles: List[Candle], dataset_version: str) -> None:
        """
        Since this contract method was defined with no return in the interface, 
        and the pipeline expects to save it, we actually want a method that just calculates.
        Let's modify the engine contract to return List[IndicatorResult] or just use a concrete method here.
        """
        pass
        
    def calculate_all(
        self, 
        candles: List[Candle], 
        dataset_version: str, 
        previous_states: Dict[str, Dict[str, Any]] = None
    ) -> List[IndicatorResult]:
        """
        Validates candles and runs them through all registered calculators.
        
        Args:
            candles: List of ascending candles.
            dataset_version: Dataset version (e.g. 'CANONICAL')
            previous_states: Dictionary mapping `indicator_type_value` -> `previous_state_dict`
                             for incremental updates.
        """
        if not candles:
            return []
            
        # 1. Validation
        IndicatorValidationEngine.validate(candles)
        
        # 2. Calculation
        all_results = []
        if previous_states is None:
            previous_states = {}
            
        for calc in self._calculators:
            try:
                # We extract the state for this specific calculator
                state = previous_states.get(calc.indicator_type.value)
                
                # We can also dynamically pass parameters here, but for now we rely on the 
                # calculator's default parameters or kwargs. In a fully dynamic system, 
                # calculators could be instantiated per configuration.
                results = calc.calculate(candles=candles, dataset_version=dataset_version, previous_state=state)
                all_results.extend(results)
                
            except Exception as e:
                logger.error(f"Calculator {calc.indicator_type.value} failed: {e}")
                # We don't swallow exceptions for deterministic orchestration
                raise
                
        return all_results
