import json
from pathlib import Path
from typing import Dict, Any


def load_all_target_to_english_dictionaries() -> Dict[str, Dict[str, Any]]:
    """
    Loads all target-to-English dictionaries from JSON files in the 'resources/lexilogos' directory.

    Returns:
    Dict[str, Dict[str, Any]]: A dictionary where the keys are language names and the values are
    merged dictionaries containing target-to-English dictionary data.
    """
    dictionaries = {}

    # Define the folder containing the JSON files
    lexilogos_folder = Path("resources/lexilogos")
    # Get all files in the folder
    lexilogos_files = lexilogos_folder.glob("*")

    for file in lexilogos_files:
        if not file.is_file():
            # Skip non-file entries
            continue

        with open(file, "r") as f:
            data = json.load(f)

        # Extract dictionaries from the loaded JSON data
        custom_target_to_english_dictionaries = data["dictionaries"][
            "custom_target_to_english"
        ]
        target_to_english_dictionaries = data["dictionaries"]["target_to_english"]

        # Merge all the dictionaries and add to the main dictionary
        language = file.stem
        dictionaries[language] = custom_target_to_english_dictionaries
        dictionaries[language].update(target_to_english_dictionaries)

    return dictionaries
