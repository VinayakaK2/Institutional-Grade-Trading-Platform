"""
String Utilities
"""
import re
from typing import Optional

class StringUtils:
    @staticmethod
    def is_blank(text: Optional[str]) -> bool:
        """Checks if a string is null, empty, or whitespace only."""
        return text is None or str(text).strip() == ""
        
    @staticmethod
    def to_snake_case(text: str) -> str:
        """Converts CamelCase to snake_case."""
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
