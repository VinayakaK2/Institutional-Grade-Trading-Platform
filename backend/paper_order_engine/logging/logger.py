import logging
from backend.paper_order_engine.models.contexts import PaperOrderExecutionContext, PaperOrderPipelineContext
from backend.paper_order_engine.utils.pipeline_version import PIPELINE_VERSION

class PaperOrderLogger:
    def __init__(self, logger_name: str = "PaperOrderEngine"):
        self.logger = logging.getLogger(logger_name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_pipeline_execution(self, execution_context: PaperOrderExecutionContext, pipeline_context: PaperOrderPipelineContext, business_fingerprint: str, snapshot_version: str):
        """
        Logs required pipeline fields while ensuring no sensitive information is leaked.
        """
        # We assume the config hash is derived deterministically from the config dict, 
        # or we just log the dictionary keys if it's safe. We can simply hash the config dict here for logging.
        import hashlib
        import json
        
        config_hash = hashlib.sha256(
            json.dumps(execution_context.configuration, sort_keys=True).encode('utf-8')
        ).hexdigest()
        
        log_data = {
            "pipeline_version": PIPELINE_VERSION,
            "configuration_hash": config_hash,
            "dataset_version": execution_context.dataset_version,
            "parent_portfolio_decision_snapshot_version": execution_context.parent_portfolio_decision_snapshot_version,
            "parent_paper_execution_snapshot_version": execution_context.parent_paper_execution_snapshot_version,
            "snapshot_version": snapshot_version,
            "order_state": pipeline_context.intermediate_order_state.value,
            "business_fingerprint": business_fingerprint
        }
        
        self.logger.info(f"Order Simulation Pipeline Completed: {json.dumps(log_data)}")
