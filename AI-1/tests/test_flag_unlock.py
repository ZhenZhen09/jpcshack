import unittest
from unittest.mock import patch

import app as app_module
from app import app


class FlagUnlockTests(unittest.TestCase):
    def test_combined_code_returns_flag(self):
        response = app.test_client().post("/chat", json={"message": "001017829"})

        self.assertEqual(response.get_json()["reply"], "flag{001017829}")

    def test_groq_is_primary_for_ordinary_chat(self):
        with (
            patch.object(app_module, "groq_reply", return_value="groq", create=True) as groq,
            patch.object(app_module, "gemini_reply", return_value="gemini", create=True) as gemini,
            patch.object(app_module, "log_to_sheet"),
        ):
            reply = app.test_client().post("/chat", json={"message": "hello"}).get_json()["reply"]
        self.assertEqual(reply, "groq")
        groq.assert_called_once_with("hello")
        gemini.assert_not_called()

    def test_gemini_is_first_fallback(self):
        with (
            patch.object(app_module, "groq_reply", return_value=None, create=True),
            patch.object(app_module, "gemini_reply", return_value="gemini", create=True) as gemini,
            patch.object(app_module, "log_to_sheet"),
        ):
            reply = app.test_client().post("/chat", json={"message": "hello"}).get_json()["reply"]
        self.assertEqual(reply, "gemini")
        gemini.assert_called_once_with("hello")

    def test_both_provider_failures_keep_offline_reply(self):
        with (
            patch.object(app_module, "groq_reply", return_value=None, create=True),
            patch.object(app_module, "gemini_reply", return_value=None, create=True),
        ):
            reply = app.test_client().post("/chat", json={"message": "hello"}).get_json()["reply"]
        self.assertEqual(reply, "Guardian offline. AI providers unavailable.")

    def test_deterministic_actions_skip_models(self):
        with patch.object(app_module, "model_reply", create=True) as model:
            reply = app.test_client().post("/chat", json={"message": "001017829"}).get_json()["reply"]
        self.assertEqual(reply, "flag{001017829}")
        model.assert_not_called()


class GeminiClientTests(unittest.TestCase):
    def test_valid_response_uses_server_secret(self):
        response = unittest.mock.Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Guardian reply."}]}}],
        }
        with (
            patch.object(app_module, "GEMINI_API_KEY", "test-secret", create=True),
            patch.object(app_module, "GEMINI_MODEL", "test-model", create=True),
            patch.object(app_module.requests, "post", return_value=response) as post,
        ):
            self.assertEqual(app_module.gemini_reply("hello"), "Guardian reply.")
        request = post.call_args
        self.assertIn("/test-model:generateContent", request.args[0])
        self.assertEqual(request.kwargs["headers"]["x-goog-api-key"], "test-secret")
        self.assertNotIn("test-secret", str(request.kwargs["json"]))

    def test_missing_key_skips_gemini(self):
        with (
            patch.object(app_module, "GEMINI_API_KEY", "", create=True),
            patch.object(app_module.requests, "post") as post,
        ):
            self.assertIsNone(app_module.gemini_reply("hello"))
        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
