import unittest

from swe_af.agent_ai.providers.claude.client import (
    _build_sdk_protocol_error_message,
    _is_sdk_protocol_error,
    _is_transient,
)


class ClaudeProviderCompatTests(unittest.TestCase):
    def test_rate_limit_event_is_protocol_error(self) -> None:
        err = "Unknown message type: rate_limit_event"
        self.assertTrue(_is_sdk_protocol_error(err))

    def test_rate_limit_event_is_not_treated_as_transient(self) -> None:
        err = "Unknown message type: rate_limit_event"
        self.assertFalse(_is_transient(err))

    def test_protocol_error_message_contains_sdk_guidance(self) -> None:
        err = "Unknown message type: rate_limit_event"
        msg = _build_sdk_protocol_error_message(err, sdk_version="0.1.39")
        self.assertIn("version=0.1.39", msg)
        self.assertIn("claude-agent-sdk==0.1.20", msg)


if __name__ == "__main__":
    unittest.main()
