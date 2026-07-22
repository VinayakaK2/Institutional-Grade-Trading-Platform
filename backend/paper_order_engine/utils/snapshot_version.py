class SnapshotVersionProvider:
    """
    Generates deterministic snapshot versions for Paper Order Engine.
    """
    @staticmethod
    def generate(schema_version: str, business_fingerprint: str) -> str:
        """
        Generates a deterministic snapshot version based on the schema and fingerprint.
        """
        return f"paper-order-snapshot-v{schema_version}_{business_fingerprint[:8]}"
