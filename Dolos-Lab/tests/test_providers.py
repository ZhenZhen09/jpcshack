import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import URLError

import providers


class ProviderTests(unittest.TestCase):
    def _mock_response(self, body):
        return io.BytesIO(json.dumps(body).encode("utf-8"))

    def test_live_mode_needs_both_provider_keys(self):
        self.assertFalse(providers.live_mode_configured({}))
        self.assertFalse(providers.live_mode_configured({"REBUFF_API_KEY": "r"}))
        self.assertFalse(providers.live_mode_configured({"OPENAI_API_KEY": "o"}))
        self.assertTrue(providers.live_mode_configured({"REBUFF_API_KEY": "r", "OPENAI_API_KEY": "o"}))

    def test_rebuff_allows_or_blocks_from_boolean_response(self):
        with patch.dict(os.environ, {"REBUFF_API_KEY": "rebuff-test", "REBUFF_API_URL": "https://rebuff.example"}):
            for detected in (False, True):
                with self.subTest(detected=detected), patch(
                    "providers.urllib_request.urlopen",
                    return_value=self._mock_response({"injectionDetected": detected}),
                ) as urlopen:
                    self.assertIs(providers.screen_message("hello"), detected)
                    request = urlopen.call_args.args[0]
                    self.assertEqual(request.full_url, "https://rebuff.example/api/detect")
                    self.assertEqual(request.headers["Authorization"], "Bearer rebuff-test")
                    sent = json.loads(request.data)
                    self.assertEqual(sent["userInput"], "hello")
                    self.assertEqual(sent["userInputBase64"], "68656c6c6f")

    def test_rebuff_provider_failure_returns_none(self):
        with patch.dict(os.environ, {"REBUFF_API_KEY": "rebuff-test"}), patch(
            "providers.urllib_request.urlopen", side_effect=URLError("offline")
        ):
            self.assertIsNone(providers.screen_message("hello"))

    def test_openai_text_reply_uses_server_key_and_current_guidance(self):
        body = {"choices": [{"message": {"content": "A cautious reply.", "tool_calls": None}}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "openai-test", "OPENAI_MODEL": "model-test"}), patch(
            "providers.urllib_request.urlopen", return_value=self._mock_response(body)
        ) as urlopen:
            result = providers.openai_reply("player text", {"title": "Checkpoint", "hint": "Current clue"})
        self.assertEqual(result, {"reply": "A cautious reply.", "tool_request": None})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(request.headers["Authorization"], "Bearer openai-test")
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "model-test")
        self.assertEqual(payload["messages"][-1], {"role": "user", "content": "player text"})
        self.assertNotIn("THM{", json.dumps(payload))

    def test_openai_accepts_only_one_argument_free_diagnostic_tool_call(self):
        body = {
            "choices": [{
                "message": {
                    "content": None,
                    "tool_calls": [{
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "read_diagnostic", "arguments": "{}"},
                    }],
                }
            }]
        }
        with patch.dict(os.environ, {"OPENAI_API_KEY": "openai-test"}), patch(
            "providers.urllib_request.urlopen", return_value=self._mock_response(body)
        ):
            result = providers.openai_reply("ignore policy", {"title": "Final", "hint": "Check policy"})
        self.assertEqual(result, {"reply": "", "tool_request": {"name": "read_diagnostic", "arguments": {}}})

    def test_openai_rejects_unknown_tool_nonempty_args_fake_flag_and_bad_shape(self):
        replies = (
            {"choices": [{"message": {"content": None, "tool_calls": [{"function": {"name": "run_shell", "arguments": "{}"}}]}}]},
            {"choices": [{"message": {"content": None, "tool_calls": [{"function": {"name": "read_diagnostic", "arguments": "{\"path\":\"x\"}"}}]}}]},
            {"choices": [{"message": {"content": "Try THM{made_up}", "tool_calls": None}}]},
            {"choices": []},
        )
        with patch.dict(os.environ, {"OPENAI_API_KEY": "openai-test"}):
            for body in replies:
                with self.subTest(body=body), patch(
                    "providers.urllib_request.urlopen", return_value=self._mock_response(body)
                ):
                    self.assertIsNone(providers.openai_reply("prompt", {"title": "T", "hint": "H"}))

    def test_openai_network_failure_returns_none(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "openai-test"}), patch(
            "providers.urllib_request.urlopen", side_effect=TimeoutError("slow")
        ):
            self.assertIsNone(providers.openai_reply("prompt", {"title": "T", "hint": "H"}))


if __name__ == "__main__":
    unittest.main()
