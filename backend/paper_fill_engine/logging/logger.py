import logging
import hashlib
import json
from backend.paper_fill_engine.models.contexts import PaperFillExecutionContext, PaperFillPipelineContext
from backend.paper_fill_engine.utils.pipeline_version import PIPELINE_VERSION

class PaperFillLogger:
    def __init__(self, logger_name: str = "PaperFillEngine"):
        self.logger = logging.getLogger(logger_name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_pipeline_execution(self, execution_context: PaperFillExecutionContext, pipeline_context: PaperFillPipelineContext, business_fingerprint: str, snapshot_version: str, fill_state: str):
        """
        Logs required pipeline fields while ensuring no sensitive information is leaked.
        """
        config_hash = hashlib.sha256(
            json.dumps(execution_context.configuration, sort_keys=True).encode('utf-8')
        ).hexdigest()
        
        log_data = {
            "pipeline_version": PIPELINE_VERSION,
            "configuration_hash": config_hash,
            "dataset_version": execution_context.dataset_version,
            "parent_paper_order_snapshot_version": execution_context.parent_paper_order_snapshot_version,
            "snapshot_version": snapshot_version,
            "fill_state": fill_state,
            "business_fingerprint": business_fingerprint
        }
        
        self.logger.info(f"Fill Simulation Pipeline Completed: {json.dumps(log_data)}")
