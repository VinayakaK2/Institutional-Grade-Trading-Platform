import json
import hashlib
from typing import Dict, Any

class SnapshotHasher:
    """
    Implements Canonical Snapshot Fingerprinting.
    Ensures stable SHA256 hashes across platforms by strictly serializing via sorted JSON.
    """
    
    @staticmethod
    def generate_fingerprint(data: Dict[str, Any]) -> str:
        """
        Recursively sorts dictionary keys and serializes to canonical JSON,
        then computes the SHA-256 fingerprint.
        """
        # default=str handles datetime, enums, etc. safely during dumps
        canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'), default=str)
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
