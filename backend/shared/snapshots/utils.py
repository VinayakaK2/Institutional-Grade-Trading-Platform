import json
import hashlib
from typing import Dict, Any

class CanonicalSerializer:
    """
    Standardizes JSON serialization across bounded contexts to ensure deterministic output.
    """
    @staticmethod
    def serialize(payload: Dict[str, Any]) -> str:
        return json.dumps(payload, sort_keys=True, separators=(',', ':'))

class HashUtility:
    """
    Standardizes ID generation for snapshots using SHA-256 hashes of canonical JSON.
    """
    @staticmethod
    def generate_id(prefix: str, payload: Dict[str, Any]) -> str:
        canonical_json = CanonicalSerializer.serialize(payload)
        return prefix + hashlib.sha256(canonical_json.encode()).hexdigest()
