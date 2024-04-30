import os
from pathlib import Path
from dotenv import load_dotenv
import deepl

dotenv_path = Path("deep_l/.env")
load_dotenv(dotenv_path=dotenv_path)

DEEPL_AUTH_KEY = os.getenv("DEEPL_AUTH_KEY")


class Translator:
    def __init__(self, auth_key) -> None:
        self.translator = deepl.Translator(auth_key)

        # Translation goes source (learner's "target language") to target
        # https://www.deepl.com/docs-api/translate-text/translate-text/
        self.source_language_codes = {
            "Arabic": "AR",
            "Bulgarian": "BG",
            "Chinese": "ZH",
            "Czech": "CS",
            "Danish": "DA",
            "Dutch": "NL",
            "English": "EN",
            "Estonian": "ET",
            "Finnish": "FI",
            "French": "FR",
            "German": "DE",
            "Greek": "EL",
            "Hungarian": "HU",
            "Indonesian": "ID",
            "Italian": "IT",
            "Japanese": "JA",
            "Korean": "KO",
            "Latvian": "LV",
            "Lithuanian": "LT",
            "Norwegian": "NB",  # (Bokmål)
            "Polish": "PL",
            "Portuguese": "PT",
            "Romanian": "RO",
            "Russian": "RU",
            "Slovak": "SK",
            "Slovenian": "SL",
            "Spanish": "ES",
            "Swedish": "SV",
            "Turkish": "TR",
            "Ukrainian": "UK",
        }

        self.target_language_codes = {
            "Arabic": "AR",
            "Bulgarian": "BG",
            "Chinese": "ZH",  # (simplified)
            "Czech": "CS",
            "Danish": "DA",
            "Dutch": "NL",
            "English": "EN-GB",
            # "English (American)": "EN-US"
            "Estonian": "ET",
            "Finnish": "FI",
            "French": "FR",
            "German": "DE",
            "Greek": "EL",
            "Hungarian": "HU",
            "Indonesian": "ID",
            "Italian": "IT",
            "Japanese": "JA",
            "Korean": "KO",
            "Latvian": "LV",
            "Lithuanian": "LT",
            "Norwegian": "NB",  # (Bokmål)
            "Polish": "PL",
            # "Brazilian Portuguese": "PT-BR"
            "Portuguese": "PT-PT",
            "Romanian": "RO",
            "Russian": "RU",
            "Slovak": "SK",
            "Slovenian": "SL",
            "Spanish": "ES",
            "Swedish": "SV",
            "Turkish": "TR",
            "Ukrainian": "UK",
        }

    def translate_text(
        self, text, source_lang, target_lang, split_sentences="off", formality="default"
    ):
        if text == "":
            return ""

        # removing soft hyphen
        if isinstance(text, str):
            text = text.replace("­", "")
        elif isinstance(text, list):
            text = [t.replace("­", "") for t in text]

        source_lang_code = self.source_language_codes[source_lang]
        target_lang_code = self.target_language_codes[target_lang]

        try:
            result = self.translator.translate_text(
                text=text,
                source_lang=source_lang_code,
                target_lang=target_lang_code,
                split_sentences=split_sentences,
                formality=formality,
            )
        except:
            result = ""
        return result


def load_translator():
    translator = Translator(DEEPL_AUTH_KEY)
    return translator
