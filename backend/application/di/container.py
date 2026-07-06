"""
Dependency Injection Container
A lightweight, production-grade IoC container supporting Singleton, Transient, and Factory lifetimes.
Includes automatic resolution via type hints and circular dependency detection.
"""
import inspect
from enum import Enum
from typing import Type, TypeVar, Callable, Dict, Any, List, Union, Optional

from backend.application.di.exceptions import DependencyResolutionException, CircularDependencyException
from backend.core.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

class Lifetime(Enum):
    TRANSIENT = "transient"
    SINGLETON = "singleton"

class ServiceDescriptor:
    def __init__(self, service_type: Type, implementation: Union[Type, Callable], lifetime: Lifetime):
        self.service_type = service_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.instance: Any = None

class Container:
    """Dependency Injection Service Container."""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}

    def register_singleton(self, service_type: Type, implementation: Optional[Union[Type, Callable]] = None) -> None:
        """Registers a service as a Singleton (one instance forever)."""
        impl = implementation or service_type
        self._services[service_type] = ServiceDescriptor(service_type, impl, Lifetime.SINGLETON)
        logger.debug(f"Registered Singleton: {service_type.__name__}")

    def register_transient(self, service_type: Type, implementation: Optional[Union[Type, Callable]] = None) -> None:
        """Registers a service as Transient (new instance on every resolve)."""
        impl = implementation or service_type
        self._services[service_type] = ServiceDescriptor(service_type, impl, Lifetime.TRANSIENT)
        logger.debug(f"Registered Transient: {service_type.__name__}")

    def resolve(self, service_type: Type[T]) -> T:
        """Resolves a service by its type, managing the dependency graph."""
        return self._resolve_internal(service_type, resolution_path=[])

    def _resolve_internal(self, service_type: Type[T], resolution_path: List[Type]) -> T:
        if service_type in resolution_path:
            path_names = " -> ".join([t.__name__ for t in resolution_path] + [service_type.__name__])
            logger.error(f"Circular dependency detected: {path_names}")
            raise CircularDependencyException(
                message=f"Circular dependency detected for {service_type.__name__}",
                details={"path": path_names}
            )
            
        if service_type not in self._services:
            raise DependencyResolutionException(f"Service {service_type.__name__} is not registered.")
            
        descriptor = self._services[service_type]
        
        # Return existing singleton if available
        if descriptor.lifetime == Lifetime.SINGLETON and descriptor.instance is not None:
            return descriptor.instance
            
        resolution_path.append(service_type)
        
        # Resolve implementation
        impl = descriptor.implementation
        
        if inspect.isclass(impl):
            # Auto-resolve constructor arguments
            sig = inspect.signature(impl.__init__)
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                    continue
                if param.annotation == inspect.Parameter.empty:
                    raise DependencyResolutionException(
                        f"Cannot resolve parameter '{param_name}' of {impl.__name__}. Missing type hint."
                    )
                # Recursively resolve dependencies
                kwargs[param_name] = self._resolve_internal(param.annotation, resolution_path)
            
            instance = impl(**kwargs)
        elif callable(impl):
            # Factory function
            instance = impl(self)
        else:
            raise DependencyResolutionException(f"Invalid implementation for {service_type.__name__}")
            
        resolution_path.pop()
        
        # Cache singleton
        if descriptor.lifetime == Lifetime.SINGLETON:
            descriptor.instance = instance
            
        return instance

# Global container instance
container = Container()
