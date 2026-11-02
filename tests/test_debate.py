import unittest
from unittest.mock import patch

from debate import DEFAULT_MODELS, run_debate, validate_debate


class DebateTests(unittest.TestCase):
    def setUp(self):
        self.participants = ["chatgpt", "claude"]
        self.keys = {"chatgpt": "test-key", "claude": "test-key", "gemini": ""}

    def test_validation_requires_two_participants(self):
        with self.assertRaisesRegex(ValueError, "두 개 이상"):
            validate_debate(
                "충분히 긴 질문",
                ["chatgpt"],
                "chatgpt",
                self.keys,
                DEFAULT_MODELS,
            )

    @patch("debate.ask_provider")
    def test_full_flow_uses_five_calls_for_two_participants(self, mock_ask):
        mock_ask.side_effect = [
            "GPT initial",
            "Claude initial",
            "GPT critique",
            "Claude critique",
            "Final synthesis",
        ]
        result = run_debate(
            "웹 토론 앱의 장단점을 분석해줘",
            self.participants,
            "chatgpt",
            self.keys,
            DEFAULT_MODELS,
        )
        self.assertEqual(len(result["answers"]), 2)
        self.assertEqual(len(result["critiques"]), 2)
        self.assertEqual(result["final_answer"], "Final synthesis")
        self.assertEqual(mock_ask.call_count, 5)


if __name__ == "__main__":
    unittest.main()
