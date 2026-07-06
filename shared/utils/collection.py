"""
Collection Utilities
"""
from typing import List, TypeVar, Iterable

T = TypeVar("T")

class CollectionUtils:
    @staticmethod
    def chunk(items: Iterable[T], size: int) -> List[List[T]]:
        """Splits an iterable into smaller chunks of a specified size."""
        lst = list(items)
        return [lst[i:i + size] for i in range(0, len(lst), size)]
