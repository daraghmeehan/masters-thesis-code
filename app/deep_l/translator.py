import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
import deepl


# Retrieving API key
dotenv_path = Path("deep_l/.env")
load_dotenv(dotenv_path=dotenv_path)
DEEPL_AUTH_KEY = os.getenv("DEEPL_AUTH_KEY")


class Translator:
    """
    A wrapper class around the DeepL API to translate text between various languages.

    Attributes:
        translator (deepl.Translator): An instance of the DeepL Translator.
        source_language_codes (dict): A dictionary mapping language names to their DeepL source language codes.
        target_language_codes (dict): A dictionary mapping language names to their DeepL target language codes.

    Reference:
        DeepL API documentation: https://developers.deepl.com/docs/api-reference/translate
    """

    def __init__(self, auth_key: str) -> None:
        """
        Initializes the Translator class with the provided authentication key.

        Args:
            auth_key (str): The API key for authenticating with the DeepL API.
        """
        self.translator = deepl.Translator(auth_key)

        # Translation goes from a source language (which is often the learner's "target language", the language of their study material) to a target language
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
            "Chinese": "ZH-HANS",  # (simplified)
            # "Chinese": "ZH-HANT",
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
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str,
        split_sentences: str = "off",
        formality: str = "default",
    ) -> List[str]:
        """
        Translates a list of texts from the source language to the target language.

        Args:
            texts (List[str]): List of texts to be translated.
            source_lang (str): The source language name.
            target_lang (str): The target language name.
            split_sentences (str, optional): Sentence splitting option for translation. Defaults to "off".
            formality (str, optional): Formality level for the translations. Defaults to "default".

        Returns:
            List[str]: List of translated texts.
        """
        if not all(isinstance(text, str) for text in texts):
            raise ValueError("All items in the 'texts' list must be strings.")

        # Removing soft hyphens
        texts = [text.replace("­", "") for text in texts]

        source_lang_code = self.source_language_codes.get(source_lang)
        target_lang_code = self.target_language_codes.get(target_lang)

        if not source_lang_code or not target_lang_code:
            raise ValueError(f"Invalid source or target language code provided.")

        try:
            # Call the DeepL API
            results = self.translator.translate_text(
                text=texts,
                source_lang=source_lang_code,
                target_lang=target_lang_code,
                split_sentences=split_sentences,
                formality=formality,
            )

            # Extract text from results
            translated_texts = [result.text for result in results]

            return translated_texts

        except deepl.DeepLException as e:
            print(f"DeepL API error: {e}")
            return [""] * len(texts)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return [""] * len(texts)


def load_translator():
    """
    Loads a Translator instance with a DeepL API key.

    Returns:
        Translator: An instance of the Translator class.
    """
    translator = Translator(DEEPL_AUTH_KEY)
    return translator
