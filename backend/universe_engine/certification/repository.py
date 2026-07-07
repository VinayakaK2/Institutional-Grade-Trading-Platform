from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
from backend.universe_engine.contracts.certification import IUniverseCertificationRepository
from backend.universe_engine.certification.models import CertificationReport, UniverseCertificationConfiguration, PerformanceMetrics
from backend.universe_engine.certification.exceptions import CertificationRepositoryError
from backend.infrastructure.database.orm.certification import CertificationReportModel

class PostgresCertificationRepository(IUniverseCertificationRepository):
    """
    SQLAlchemy-based repository for persisting Certification Reports.
    """
    
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        
    async def save_certification_report(self, report: CertificationReport) -> None:
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    db_model = CertificationReportModel(
                        certification_id=report.certification_id,
                        pipeline_version=report.pipeline_version,
                        config_hash=report.config_hash,
                        business_fingerprint_version=report.business_fingerprint_version,
                        git_commit_hash=report.git_commit_hash,
                        created_at=report.created_at,
                        configuration_snapshot=report.configuration_snapshot.model_dump(mode='json'),
                        functional_passed=report.functional_passed,
                        determinism_passed=report.determinism_passed,
                        integrity_passed=report.integrity_passed,
                        stress_passed=report.stress_passed,
                        is_certified=report.is_certified,
                        test_results=report.test_results,
                        determinism_results=report.determinism_results,
                        performance_metrics=report.performance_metrics.model_dump(mode='json')
                    )
                    session.add(db_model)
        except Exception as e:
            raise CertificationRepositoryError(f"Failed to save certification report: {str(e)}") from e
            
    async def load_certification_report(self, certification_id: str) -> CertificationReport:
        try:
            async with self._session_factory() as session:
                stmt = select(CertificationReportModel).where(CertificationReportModel.certification_id == certification_id)
                result = await session.execute(stmt)
                db_model = result.scalar_one_or_none()
                
                if not db_model:
                    raise ValueError(f"CertificationReport {certification_id} not found.")
                    
                from typing import cast, Dict, Any, Optional
                from datetime import datetime
                return CertificationReport(
                    certification_id=cast(str, db_model.certification_id),
                    pipeline_version=cast(str, db_model.pipeline_version),
                    config_hash=cast(str, db_model.config_hash),
                    business_fingerprint_version=cast(str, db_model.business_fingerprint_version),
                    git_commit_hash=cast(Optional[str], db_model.git_commit_hash),
                    created_at=cast(datetime, db_model.created_at),
                    configuration_snapshot=UniverseCertificationConfiguration(**cast(Dict[str, Any], db_model.configuration_snapshot)),
                    functional_passed=cast(bool, db_model.functional_passed),
                    determinism_passed=cast(bool, db_model.determinism_passed),
                    integrity_passed=cast(bool, db_model.integrity_passed),
                    stress_passed=cast(bool, db_model.stress_passed),
                    is_certified=cast(bool, db_model.is_certified),
                    test_results=cast(Dict[str, Any], db_model.test_results),
                    determinism_results=cast(Dict[str, Any], db_model.determinism_results),
                    performance_metrics=PerformanceMetrics(**cast(Dict[str, Any], db_model.performance_metrics))
                )
        except ValueError:
            raise
        except Exception as e:
            raise CertificationRepositoryError(f"Failed to load certification report {certification_id}: {str(e)}") from e
