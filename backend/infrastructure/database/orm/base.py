"""
ORM Base Configuration
Defines the SQLAlchemy Declarative Base and global naming conventions.
"""
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Enforce consistent naming conventions for database constraints.
# This prevents Alembic from generating random names for constraints,
# which causes migration issues across different environments.
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

class Base(DeclarativeBase):
    """
    The root DeclarativeBase for the entire platform.
    All models must inherit from this or a subclass of this.
    """
    metadata = metadata
