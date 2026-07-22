from backend.portfolio_certification_framework.contracts.pipeline import IPortfolioCertificationStage
from backend.portfolio_certification_framework.models.contexts import PortfolioCertificationExecutionContext
from backend.portfolio_certification_framework.verification.functional import verify_functional
from backend.portfolio_certification_framework.verification.determinism import verify_determinism
from backend.portfolio_certification_framework.verification.repository import verify_repository
from backend.portfolio_certification_framework.verification.stress import verify_stress
from backend.portfolio_certification_framework.verification.performance import verify_performance
from backend.portfolio_certification_framework.verification.regression import verify_regression
import logging

logger = logging.getLogger(__name__)

class FunctionalVerificationStage(IPortfolioCertificationStage):
    async def execute(self, context: PortfolioCertificationExecutionContext) -> None:
        logger.info("[Certification] Executing Functional Verification Stage")
        result = await verify_functional(context)
        context.stage_results.append(result)

class DeterminismVerificationStage(IPortfolioCertificationStage):
    async def execute(self, context: PortfolioCertificationExecutionContext) -> None:
        logger.info("[Certification] Executing Determinism Verification Stage")
        result = await verify_determinism(context)
        context.stage_results.append(result)

class RepositoryVerificationStage(IPortfolioCertificationStage):
    async def execute(self, context: PortfolioCertificationExecutionContext) -> None:
        logger.info("[Certification] Executing Repository Verification Stage")
        result = await verify_repository(context)
        context.stage_results.append(result)

class StressVerificationStage(IPortfolioCertificationStage):
    async def execute(self, context: PortfolioCertificationExecutionContext) -> None:
        logger.info("[Certification] Executing Stress Verification Stage")
        result = await verify_stress(context)
        context.stage_results.append(result)

class PerformanceVerificationStage(IPortfolioCertificationStage):
    async def execute(self, context: PortfolioCertificationExecutionContext) -> None:
        logger.info("[Certification] Executing Performance Verification Stage")
        result = await verify_performance(context)
        context.stage_results.append(result)

class RegressionVerificationStage(IPortfolioCertificationStage):
    async def execute(self, context: PortfolioCertificationExecutionContext) -> None:
        logger.info("[Certification] Executing Regression Verification Stage")
        result = await verify_regression(context)
        context.stage_results.append(result)
