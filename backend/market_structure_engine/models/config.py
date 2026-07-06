from enum import Enum
from pydantic import BaseModel, ConfigDict

class ConfirmationRule(str, Enum):
    WICK_BREAK = "wick_break"
    BODY_CLOSE = "body_close"

class StructureConfig(BaseModel):
    """
    Configuration for detecting BoS and ChoCH events.
    """
    model_config = ConfigDict(frozen=True)
    confirmation_rule: ConfirmationRule = ConfirmationRule.BODY_CLOSE
