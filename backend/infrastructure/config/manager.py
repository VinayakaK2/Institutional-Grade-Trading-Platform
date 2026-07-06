"""
Configuration Manager
"""
from typing import TypeVar, Type, Dict, cast
from backend.core.logger import get_logger
from backend.infrastructure.config.settings import AppSettings

logger = get_logger(__name__)

T = TypeVar("T", bound=AppSettings)

class ConfigurationManager:
    """
    Manages loading and validating strongly-typed configuration classes.
    """
    
    def __init__(self):
        self._configs: Dict[Type, AppSettings] = {}

    def load(self, config_class: Type[T]) -> T:
        """
        Loads, validates, and caches a configuration class.
        """
        if config_class not in self._configs:
            logger.info(f"Loading configuration for {config_class.__name__}")
            try:
                # Pydantic BaseSettings automatically reads from env/kwargs
                instance = config_class()
                self._configs[config_class] = instance
                logger.info(f"Successfully loaded {config_class.__name__}")
            except Exception as e:
                logger.critical(f"Configuration validation failed for {config_class.__name__}", exc_info=True)
                raise RuntimeError(f"Config validation failed: {e}") from e
                
        return cast(T, self._configs[config_class])

# Global Configuration Manager
config_manager = ConfigurationManager()
