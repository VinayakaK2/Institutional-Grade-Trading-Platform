"""
Cache Key Builder
Standardizes cache key generation to avoid collisions across namespaces.
"""
class CacheKeyBuilder:
    @staticmethod
    def build(namespace: str, entity: str, identifier: str) -> str:
        """
        Builds a standard cache key.
        Format: {namespace}:{entity}:{identifier}
        """
        return f"{namespace}:{entity}:{identifier}".lower()
