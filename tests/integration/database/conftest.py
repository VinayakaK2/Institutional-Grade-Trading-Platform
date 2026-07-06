"""
Database Tests Configuration
"""

from backend.infrastructure.database.orm.models import AuditableModel, SoftDeleteModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

# Create a test-only model to verify the base mixins without introducing business logic
class DummyAuditableModel(AuditableModel):
    dummy_name: Mapped[str] = mapped_column(String(50))

class DummySoftDeleteModel(SoftDeleteModel):
    dummy_name: Mapped[str] = mapped_column(String(50))


