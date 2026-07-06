"""
Integration Tests for Dependency Injection
"""
import pytest
from backend.application.di.container import Container
from backend.application.di.exceptions import DependencyResolutionException, CircularDependencyException

class ServiceA:
    pass

class ServiceB:
    def __init__(self, a: ServiceA):
        self.a = a

class CircularA:
    def __init__(self, b: 'CircularB'):
        self.b = b

class CircularB:
    def __init__(self, a: 'CircularA'):
        self.a = a


def test_di_singleton_resolution():
    container = Container()
    container.register_singleton(ServiceA)
    container.register_singleton(ServiceB)

    instance1 = container.resolve(ServiceB)
    instance2 = container.resolve(ServiceB)

    assert isinstance(instance1, ServiceB)
    assert isinstance(instance1.a, ServiceA)
    # Singletons should return the exact same instance in memory
    assert instance1 is instance2
    assert instance1.a is instance2.a

def test_di_transient_resolution():
    container = Container()
    container.register_transient(ServiceA)
    container.register_transient(ServiceB)

    instance1 = container.resolve(ServiceB)
    instance2 = container.resolve(ServiceB)

    assert isinstance(instance1, ServiceB)
    # Transients should be different instances
    assert instance1 is not instance2
    assert instance1.a is not instance2.a

def test_di_circular_dependency():
    container = Container()
    # Annotations as strings won't resolve automatically with standard inspect easily unless we parse strings, 
    # but let's test a direct circular link.
    
    # We will simulate standard circular dependency without string hints for testing
    class LoopA: 
        pass
    class LoopB: 
        pass
    
    LoopA.__init__ = lambda self, b: None
    LoopA.__init__.__annotations__ = {'b': LoopB}
    
    LoopB.__init__ = lambda self, a: None
    LoopB.__init__.__annotations__ = {'a': LoopA}
    
    container.register_transient(LoopA)
    container.register_transient(LoopB)
    
    with pytest.raises(CircularDependencyException):
        container.resolve(LoopA)

def test_di_unregistered_resolution():
    container = Container()
    with pytest.raises(DependencyResolutionException):
        container.resolve(ServiceA)
