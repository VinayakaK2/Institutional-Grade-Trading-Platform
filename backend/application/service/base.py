"""
Base Service Layer
Abstracts the execution pipeline for domain services, ensuring validation 
and Unit of Work context management wrap every business operation.
"""
from typing import Any, Callable, Coroutine, TypeVar, List, Optional
from backend.application.uow.base import BaseUnitOfWork
from backend.application.validation.pipeline import ValidationPipeline, ValidationRule
from backend.core.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

class BaseService:
    """
    Abstract base service that provides structured execution pipelines.
    Services encapsulate business logic, orchestrate repositories via the UoW,
    and enforce validation rules.
    """
    
    def __init__(self, uow: BaseUnitOfWork):
        self._uow = uow

    async def execute_in_transaction(
        self, 
        operation: Callable[[BaseUnitOfWork], Coroutine[Any, Any, T]],
        validation_target: Any = None,
        validation_rules: Optional[List[ValidationRule]] = None
    ) -> T:
        """
        Executes an operation within a Unit of Work transaction.
        Optionally runs a validation pipeline before execution.
        """
        logger.debug(f"Executing service operation in transaction: {self.__class__.__name__}")
        
        # 1. Validation Phase
        if validation_target is not None and validation_rules:
            pipeline = ValidationPipeline()
            for rule in validation_rules:
                pipeline.add_rule(rule)
            await pipeline.execute(validation_target)
            
        # 2. Execution Phase
        async with self._uow as uow:
            result = await operation(uow)
            await uow.commit()
            return result
