from typing import List, Optional

from backend.market_data.models.candle import Candle
from backend.corporate_actions.models.action import CorporateAction, ActionType
from backend.corporate_actions.models.adjustment import AdjustmentMode
from backend.corporate_actions.adjustment.calculators import (
    BaseAdjustment, SplitAdjustment, ReverseSplitAdjustment, BonusAdjustment, DividendAdjustment
)

class AdjustmentEngine:
    """Applies corporate actions to a dataset chronologically backwards."""
    
    def __init__(self):
        pass
        
    def adjust(self, dataset: List[Candle], actions: List[CorporateAction], mode: AdjustmentMode) -> List[Candle]:
        """
        Adjusts a list of canonical candles based on the provided corporate actions.
        Assumes `dataset` is sorted chronologically (oldest to newest).
        """
        if mode == AdjustmentMode.RAW or not actions:
            return dataset
            
        # We need to process backwards from the most recent to the oldest
        adjusted_dataset = []
        
        # Sort actions by effective date descending (newest first)
        sorted_actions = sorted(actions, key=lambda a: a.effective_date, reverse=True)
        
        # We iterate over the dataset from newest to oldest to apply adjustments correctly
        # because an adjustment at T affects all candles < T.
        # But wait, it's easier to iterate the dataset and for each candle, find all actions > candle.timestamp
        # and apply them.
        
        # Let's group actions. But proportional dividends require knowing the close price *prior* to the ex-date.
        # So we should calculate the adjustment factor for each action first.
        # Actually, for splits it's just a constant ratio.
        # For dividends, it's 1 - (dividend / close_prior).
        
        # Pre-compute calculators for each action
        action_calculators: List[tuple] = [] # (CorporateAction, BaseAdjustment)
        
        # Find close prior for dividends
        for action in sorted_actions:
            calc = self._get_calculator(action, dataset)
            if calc:
                action_calculators.append((action, calc))
                
        # Now apply to each candle
        for candle in dataset:
            current_candle = candle
            candle_date = candle.timestamp.date()
            
            # Apply all actions that became effective AFTER this candle's date.
            # E.g. Split on 2024-05-02. A candle on 2024-05-01 needs adjustment.
            # A candle on 2024-05-02 does NOT need adjustment (it already reflects the split).
            for action, calculator in action_calculators:
                if candle_date < action.effective_date:
                    adjusted_candle = calculator.adjust(current_candle, action)
                    
                    # Respect AdjustmentMode
                    if mode == AdjustmentMode.PRICE_ADJUSTED_ONLY:
                        adjusted_candle.volume = current_candle.volume
                    elif mode == AdjustmentMode.VOLUME_ADJUSTED_ONLY:
                        adjusted_candle.open = current_candle.open
                        adjusted_candle.high = current_candle.high
                        adjusted_candle.low = current_candle.low
                        adjusted_candle.close = current_candle.close
                        
                    current_candle = adjusted_candle
                    
            adjusted_dataset.append(current_candle)
            
        return adjusted_dataset

    def _get_calculator(self, action: CorporateAction, dataset: List[Candle]) -> Optional[BaseAdjustment]:
        if action.action_type == ActionType.STOCK_SPLIT:
            return SplitAdjustment()
        elif action.action_type == ActionType.REVERSE_SPLIT:
            return ReverseSplitAdjustment()
        elif action.action_type == ActionType.BONUS_ISSUE:
            return BonusAdjustment()
        elif action.action_type == ActionType.CASH_DIVIDEND:
            # Find the close price immediately prior to the effective date
            # Dataset is assumed oldest to newest.
            prior_close = 0.0
            for candle in reversed(dataset):
                if candle.timestamp.date() < action.effective_date:
                    prior_close = candle.close
                    break
            return DividendAdjustment(close_prior_to_ex_date=prior_close)
        
        return None
