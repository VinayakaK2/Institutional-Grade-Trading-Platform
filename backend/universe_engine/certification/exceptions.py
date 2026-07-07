class CertificationVerificationError(Exception):
    """
    Raised when a critical certification verification check fails.
    Used to halt the pipeline if the failure is unrecoverable,
    otherwise standard verification failures are recorded in the context without raising.
    """
    pass

class CertificationRepositoryError(Exception):
    """Raised for errors interacting with the Certification Repository."""
    pass
