import uuid

class SnapshotVersionProvider:
    @staticmethod
    def generate() -> str:
        return f"paper-execution-quality-snapshot-{uuid.uuid4().hex}"
