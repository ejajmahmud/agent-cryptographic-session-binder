"""Unit tests for agent-cryptographic-session-binder."""
import unittest
from agent_cryptographic_session_binder.binder import AgentCryptographicSessionBinder


class TestAgentCryptographicSessionBinder(unittest.TestCase):
    def setUp(self):
        self.key = b"test_key_abc_123"
        self.binder = AgentCryptographicSessionBinder(self.key)

    def test_seal_and_verify(self):
        env = self.binder.seal({"data": 1}, seq=1)
        self.assertTrue(self.binder.verify(env))

    def test_tamper_payload_fails(self):
        env = self.binder.seal({"data": 1}, seq=1)
        env.payload["data"] = 999  # Tampered!
        self.assertFalse(self.binder.verify(env))

    def test_replay_rejected(self):
        env = self.binder.seal({"data": 1}, seq=1)
        self.assertTrue(self.binder.verify(env))
        self.assertFalse(self.binder.verify(env))
