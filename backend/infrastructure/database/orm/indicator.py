from sqlalchemy import Column, String, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.infrastructure.database.orm.base import Base

class IndicatorOrm(Base):
    __tablename__ = 'indicators'

    # Composite primary key elements for deterministic uniqueness
    symbol_id = Column(String, primary_key=True, index=True)
    timeframe = Column(String, primary_key=True, index=True)
    dataset_version = Column(String, primary_key=True, index=True)
    timestamp = Column(String, primary_key=True, index=True)
    indicator_type = Column(String, primary_key=True, index=True)
    param_key = Column(String, primary_key=True, index=True)
    
    # Values
    parameters = Column(JSON, nullable=False)
    value = Column(Float, nullable=False)
    internal_state = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<IndicatorOrm(symbol={self.symbol_id}, type={self.indicator_type}, val={self.value})>"
