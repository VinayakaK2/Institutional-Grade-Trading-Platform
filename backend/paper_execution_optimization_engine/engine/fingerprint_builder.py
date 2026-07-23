import hashlib
from backend.paper_execution_optimization_engine.models.contexts import PaperExecutionOptimizationContext
from backend.paper_execution_optimization_engine.config.config import OPTIMIZATION_ENGINE_VERSION

class OptimizationFingerprintBuilder:
    """
    Generates deterministic fingerprints for optimization context caching.
    """

    @staticmethod
    def build(context: PaperExecutionOptimizationContext) -> str:
        """
        Builds a deterministic optimization fingerprint.
        Relies strictly on canonical properties to ensure consistency.
        Never uses string representations of dictionaries.
        """
        
        # 1. Business Execution Fingerprint (Already deterministic and pre-computed or derivable)
        # Note: The context contains `PaperExecutionResultExecutionContext`. 
        # This context is what gets sent into the result engine. The result engine uses its inputs
        # to generate a fingerprint. We need a way to identify the inputs uniquely here.
        # Assuming PaperExecutionResultExecutionContext has a method or property for business fingerprinting,
        # or we hash its canonical fields. Wait, PaperExecutionResultExecutionContext is just a container.
        # Let's compute a hash of its core identifying properties if it doesn't have a fingerprint itself.
        
        # We need to extract the dataset_version and pipeline_version and the parent snapshot fingerprints.
        dataset_version = context.execution_context.dataset_version
        
        # Since the context has paper_order_snapshot and paper_fill_snapshot:
        order_fingerprint = context.execution_context.paper_order_snapshot.business_fingerprint
        fill_fingerprint = context.execution_context.paper_fill_snapshot.business_fingerprint
        
        # The configuration hash
        config_caching = str(context.optimization_configuration.caching_enabled).lower()
        
        # We combine them in a strict canonical string formatting
        payload = (
            f"ds={dataset_version}|"
            f"opt_v={OPTIMIZATION_ENGINE_VERSION}|"
            f"order={order_fingerprint}|"
            f"fill={fill_fingerprint}|"
            f"cache={config_caching}"
        )
        
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()
