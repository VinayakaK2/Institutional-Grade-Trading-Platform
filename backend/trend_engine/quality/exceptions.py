"""
Trend Quality Engine Exceptions
===============================

Defines the exception hierarchy for the Trend Quality Engine.
"""

class TrendQualityException(Exception):
    """Base exception for all Trend Quality Engine errors."""
    pass


class InvalidQualityConfigurationError(TrendQualityException):
    """Raised when the TrendQualityConfig fails validation or contains illogical bounds."""
    pass


class QualityRepositoryError(TrendQualityException):
    """Base exception for all repository-related failures within the Quality Engine."""
    pass


class MissingParentTrendError(QualityRepositoryError):
    """Raised when attempting to evaluate a trend snapshot that does not exist or is inaccessible."""
    pass


class DuplicateQualityEvaluationError(QualityRepositoryError):
    """Raised when an attempt is made to overwrite an existing TrendQualitySnapshot in the repository."""
    pass


class IncompleteQualityEvaluationError(TrendQualityException):
    """Raised when a quality evaluation stage returns incomplete metrics preventing aggregation."""
    pass
