"""
UUID Utilities
"""
import uuid

class UUIDUtils:
    @staticmethod
    def generate() -> str:
        """Generates a UUID4 string."""
        return str(uuid.uuid4())
        
    @staticmethod
    def is_valid(val: str) -> bool:
        """Checks if a string is a valid UUID4."""
        try:
            uuid_obj = uuid.UUID(val, version=4)
            return str(uuid_obj) == val
        except ValueError:
            return False
