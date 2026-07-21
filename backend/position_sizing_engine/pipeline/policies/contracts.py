import abc

class IRoundLotPolicy(abc.ABC):
    """
    Contract for rounding asset quantities.
    """
    @abc.abstractmethod
    def apply(self, raw_size: float) -> float:
        pass
        
    @property
    @abc.abstractmethod
    def policy_name(self) -> str:
        pass
