import asyncio
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any, Callable, Tuple
from backend.market_data.models.candle import Candle
from backend.indicator_engine.models.indicator import IndicatorResult
from backend.indicator_engine.contracts.calculator import IndicatorCalculatorContract

logger = logging.getLogger(__name__)

def _execute_calculator(
    calculator_cls: type,
    candles: List[Candle],
    dataset_version: str,
    previous_state: Dict[str, Any],
    kwargs: Dict[str, Any]
) -> List[IndicatorResult]:
    """
    Top-level function for multiprocessing.
    Instantiates the calculator and runs the calculation.
    """
    try:
        calc = calculator_cls()
        return calc.calculate(
            candles=candles,
            dataset_version=dataset_version,
            previous_state=previous_state,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Failed to calculate {calculator_cls.__name__}: {e}")
        # We return an exception object to handle it in the orchestrator
        return e

class ParallelExecutionEngine:
    """
    Executes indicator calculations in parallel using a ProcessPoolExecutor.
    Isolates failures and returns results deterministically.
    """
    def __init__(self, max_workers: int = None):
        self._max_workers = max_workers or max(1, multiprocessing.cpu_count() - 1)
        self._pool = ProcessPoolExecutor(max_workers=self._max_workers)
        
    async def execute_batch(
        self,
        tasks: List[Tuple[type, List[Candle], str, Dict[str, Any], Dict[str, Any]]]
    ) -> List[List[IndicatorResult]]:
        """
        Executes a batch of calculation tasks in parallel.
        
        Args:
            tasks: List of Tuples containing:
                   (calculator_class, candles, dataset_version, previous_state, kwargs)
                   
        Returns:
            List of result lists in the same order as tasks.
        """
        if not tasks:
            return []
            
        loop = asyncio.get_running_loop()
        futures = []
        
        for task in tasks:
            calc_cls, candles, version, prev_state, kwargs = task
            future = loop.run_in_executor(
                self._pool,
                _execute_calculator,
                calc_cls,
                candles,
                version,
                prev_state,
                kwargs
            )
            futures.append(future)
            
        results = await asyncio.gather(*futures, return_exceptions=True)
        
        final_results = []
        for res in results:
            if isinstance(res, Exception):
                # Isolate failure, don't crash the whole batch
                logger.error(f"Task failed in ParallelExecutionEngine: {res}")
                final_results.append([])
            else:
                final_results.append(res)
                
        return final_results
        
    def shutdown(self):
        self._pool.shutdown(wait=True)
