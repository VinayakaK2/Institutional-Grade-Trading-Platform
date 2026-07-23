import uuid

class SnapshotVersionProvider:
    @staticmethod
    def generate() -> str:
        return f"exec_res_{uuid.uuid4().hex}"
