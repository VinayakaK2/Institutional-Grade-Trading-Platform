from typing import List
from backend.historical_data.models.raw import RawCandle
from backend.data_validation.contracts.rule import ValidationRule, ValidationContext
from backend.data_validation.models.report import ValidationResult
from backend.historical_data.engine.normalizer import DataNormalizer

class AnomalyDetector(ValidationRule):
    """
    Detects extreme price and volume spikes.
    Thresholds are provided via context.dependencies['anomaly_config'].
    """
    async def validate(self, context: ValidationContext, records: List[RawCandle]) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        if not records:
            return results
            
        config = context.dependencies.get('anomaly_config', {})
        max_price_change_pct = config.get('max_price_change_pct', 50.0) # 50% change is suspicious
        max_volume_spike_ratio = config.get('max_volume_spike_ratio', 100.0) # 100x previous volume is suspicious
        
        # Sort and parse
        valid_records = []
        for r in records:
            try:
                dt = DataNormalizer._parse_timestamp(r.raw_timestamp)
                c = float(r.raw_close)
                v = float(r.raw_volume)
                valid_records.append((dt, c, v, r))
            except Exception:
                continue # nosec B112
                
        valid_records.sort(key=lambda x: x[0])
        
        if len(valid_records) < 2:
            return results
            
        for i in range(1, len(valid_records)):
            _, prev_close, prev_vol, _ = valid_records[i-1]
            dt, curr_close, curr_vol, curr_record = valid_records[i]
            
            # Price Anomaly
            if prev_close > 0:
                change_pct = abs(curr_close - prev_close) / prev_close * 100
                if change_pct > max_price_change_pct:
                    results.append(ValidationResult(
                        rule_name="AnomalyDetector.ExtremePriceChange",
                        is_valid=False,
                        record_timestamp=str(curr_record.raw_timestamp),
                        message=f"Extreme price change detected: {change_pct:.2f}% (Threshold: {max_price_change_pct}%)"
                    ))
                    
            # Volume Anomaly
            if prev_vol > 0:
                vol_ratio = curr_vol / prev_vol
                if vol_ratio > max_volume_spike_ratio:
                    results.append(ValidationResult(
                        rule_name="AnomalyDetector.ExtremeVolumeSpike",
                        is_valid=False,
                        record_timestamp=str(curr_record.raw_timestamp),
                        message=f"Extreme volume spike detected: {vol_ratio:.2f}x (Threshold: {max_volume_spike_ratio}x)"
                    ))
                    
        return results
