class DataQualityFilterError(Exception):
    """Base exception for all errors in the Data Quality Filter module."""

    pass


class DataQualityPipelineError(DataQualityFilterError):
    """Raised when the Data Quality Filter Pipeline encounters an unexpected orchestration error."""

    pass


class MissingDataQualityDataError(DataQualityFilterError):
    """Raised when a data provider fails to return necessary data for data quality evaluation."""

    pass


class MissingMarketCalendarError(DataQualityFilterError):
    """Raised when the market calendar provider fails to return valid trading sessions."""

    pass


class InvalidConfigurationError(DataQualityFilterError):
    """Raised when the data quality configuration is logically invalid."""

    pass


class DataQualityRepositoryError(DataQualityFilterError):
    """Raised when persisting or loading a Certified Universe fails."""

    pass
