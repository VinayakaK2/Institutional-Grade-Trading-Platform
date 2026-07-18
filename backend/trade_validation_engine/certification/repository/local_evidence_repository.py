import json
import os
import uuid
from typing import Dict, Any
from backend.trade_validation_engine.certification.contracts.repository import ICertificationRepository
from backend.trade_validation_engine.certification.models.models import CertificationReport
from backend.trade_validation_engine.certification.config.config import CertificationConfig

class LocalEvidenceRepository(ICertificationRepository):
    """
    Persists certification reports and raw evidence as JSON files locally.
    """
    def __init__(self, config: CertificationConfig):
        self._output_dir = config.report_output_directory
        self._evidence_dir = os.path.join(self._output_dir, "evidence")
        
        # Ensure directories exist
        os.makedirs(self._evidence_dir, exist_ok=True)
        
    async def save_report(self, report: CertificationReport) -> None:
        file_name = f"certification_report_{report.certification_id}.json"
        path = os.path.join(self._output_dir, file_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))
            
    async def save_evidence(self, stage_name: str, evidence: Dict[str, Any]) -> str:
        safe_name = stage_name.lower().replace(" ", "_").replace(":", "")
        file_name = f"{safe_name}_{uuid.uuid4().hex[:8]}.json"
        path = os.path.join(self._evidence_dir, file_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(evidence, f, indent=2, default=str)
        return path
