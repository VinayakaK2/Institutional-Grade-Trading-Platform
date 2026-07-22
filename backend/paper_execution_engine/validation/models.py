from typing import List
from pydantic import BaseModel, Field, StrictStr, StrictBool

class ValidationReport(BaseModel):
    """
    Structured validation report.
    """
    passed: StrictBool
    errors: List[StrictStr] = Field(default_factory=list)
    warnings: List[StrictStr] = Field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.passed = False
        
    def add_warning(self, message: str) -> None:
        self.warnings.append(message)
