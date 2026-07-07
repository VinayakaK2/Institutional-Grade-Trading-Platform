from sqlalchemy import Column, String, DateTime, Boolean, JSON
from backend.infrastructure.database.orm.base import Base

class CertificationReportModel(Base):
    """
    SQLAlchemy ORM model for CertificationReport.
    """
    __tablename__ = "certification_reports"
    
    certification_id = Column(String, primary_key=True)
    pipeline_version = Column(String, nullable=False)
    config_hash = Column(String, nullable=False)
    business_fingerprint_version = Column(String, nullable=False)
    git_commit_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    
    configuration_snapshot = Column(JSON, nullable=False)
    
    functional_passed = Column(Boolean, nullable=False)
    determinism_passed = Column(Boolean, nullable=False)
    integrity_passed = Column(Boolean, nullable=False)
    stress_passed = Column(Boolean, nullable=False)
    is_certified = Column(Boolean, nullable=False)
    
    test_results = Column(JSON, nullable=False)
    determinism_results = Column(JSON, nullable=False)
    performance_metrics = Column(JSON, nullable=False)
