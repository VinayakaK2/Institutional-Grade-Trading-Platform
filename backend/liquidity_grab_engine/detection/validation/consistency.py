from typing import Any

class DetectionConsistencyValidator:
    """
    Validates the consistency of the detection context, such as dataset lineage
    and snapshot compatibility. Does not evaluate business logic or quality.
    """
    
    @staticmethod
    def validate(context: Any) -> None:
        if context.dataset.version <= 0:
            raise ValueError("Invalid dataset version. Must be > 0.")
            
        if context.parent_snapshots.trend_snapshot_version <= 0:
            raise ValueError("Invalid parent trend snapshot version. Must be > 0.")
            
        if context.parent_snapshots.consolidation_snapshot_version <= 0:
            raise ValueError("Invalid parent consolidation snapshot version. Must be > 0.")
