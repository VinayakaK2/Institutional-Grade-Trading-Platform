class CertificationFailedError(Exception):
    """Raised when any certification stage fundamentally fails validation."""
    pass

class SnapshotCorruptionError(Exception):
    """Raised when repository verification detects broken append-only constraints or tampered historical records."""
    pass

class CertificationRepositoryIntegrityError(Exception):
    """Raised by repositories on constraint violations (e.g., duplicated canonical hashes if not handled)."""
    pass

class CertificationRepositoryNotFoundError(Exception):
    """Raised when a specific certification record cannot be loaded."""
    pass
