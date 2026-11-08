"""Core Agent Cryptographic Session Binder implementation."""
import hmac
import hashlib
import json
import time
from typing import Dict, Any, Optional


class SignedEnvelope:
    def __init__(self, payload: Dict[str, Any], seq: int, timestamp: float, signature: str):
        self.payload = payload
        self.seq = seq
        self.timestamp = timestamp
        self.signature = signature

    def to_dict(self) -> Dict[str, Any]:
        return {
            "payload": self.payload,
            "seq": self.seq,
            "timestamp": self.timestamp,
            "signature": self.signature
        }


class AgentCryptographicSessionBinder:
    def __init__(self, session_key: bytes, max_clock_skew: float = 60.0):
        self.session_key = session_key
        self.max_clock_skew = max_clock_skew
        self.last_seen_seq = -1

    def _compute_hmac(self, canonical_string: str) -> str:
        return hmac.new(self.session_key, canonical_string.encode("utf-8"), hashlib.sha256).hexdigest()

    def seal(self, payload: Dict[str, Any], seq: int) -> SignedEnvelope:
        ts = time.time()
        serialized_payload = json.dumps(payload, sort_keys=True)
        canonical = f"{seq}:{ts:.3f}:{serialized_payload}"
        sig = self._compute_hmac(canonical)
        return SignedEnvelope(payload, seq, ts, sig)

    def verify(self, envelope: SignedEnvelope) -> bool:
        # 1. Monotonic sequence check
        if envelope.seq <= self.last_seen_seq:
            return False  # Replay detected

        # 2. Clock skew check
        now = time.time()
        if abs(now - envelope.timestamp) > self.max_clock_skew:
            return False

        # 3. Signature verification
        serialized_payload = json.dumps(envelope.payload, sort_keys=True)
        canonical = f"{envelope.seq}:{envelope.timestamp:.3f}:{serialized_payload}"
        expected_sig = self._compute_hmac(canonical)

        if hmac.compare_digest(expected_sig, envelope.signature):
            self.last_seen_seq = envelope.seq
            return True
        return False
