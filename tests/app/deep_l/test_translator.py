import unittest
from unittest.mock import patch, MagicMock
from app.deep_l.translator import Translator


class MockTextResult:
    def __init__(self, text):
        self.text = text


def mock_translate_text(text, source_lang, target_lang, *args, **kwargs):
    translations = {
        ("¿Cómo estás?", "ES", "EN-GB"): ["How are you?"],
        ("uno", "ES", "EN-GB"): ["one"],
    }

    def translate(item):
        return MockTextResult(
            translations.get((item, source_lang, target_lang), ["Unknown"])[0]
        )

    if isinstance(text, list):
        return [translate(t) for t in text]
    else:
        return translate(text)


class TestTranslator(unittest.TestCase):
    @patch("app.deep_l.translator.Translator.translate_text")
    def test_translate_text(self, mock_translate):
        mock_translate.side_effect = mock_translate_text

        translator = Translator("dummy_key")

        # Test translating one sentence
        result = translator.translate_text("¿Cómo estás?", "ES", "EN-GB")
        self.assertEqual([r.text for r in result], ["How are you?"])

        # Test translating multiple sentences
        result = translator.translate_text(["¿Cómo estás?", "uno"], "ES", "EN-GB")
        self.assertEqual([r.text for r in result], ["How are you?", "one"])


if __name__ == "__main__":
    unittest.main()
