import unittest
from unittest.mock import patch, MagicMock
from app.deep_l.translator import Translator


class MockTextResult:
    def __init__(self, text, detected_source_lang):
        self.text = text
        self.detected_source_lang = detected_source_lang


def mock_translate_text(text, source_lang, target_lang, *args, **kwargs):
    translations = {
        ("¿Cómo estás?", "ES", "EN-GB"): ("How are you?", "ES"),
        ("uno", "ES", "EN-GB"): ("one", "ES"),
    }

    def translate(item):
        result = translations.get(
            (item, source_lang, target_lang), ("Unknown", "Unknown")
        )
        return MockTextResult(*result)

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
        self.assertEqual(result.text, "How are you?")
        self.assertEqual(result.detected_source_lang, "ES")

        # Test translating multiple sentences
        result = translator.translate_text(["¿Cómo estás?", "uno"], "ES", "EN-GB")
        self.assertEqual(result[0].text, "How are you?")
        self.assertEqual(result[0].detected_source_lang, "ES")
        self.assertEqual(result[1].text, "one")
        self.assertEqual(result[1].detected_source_lang, "ES")


if __name__ == "__main__":
    unittest.main()
