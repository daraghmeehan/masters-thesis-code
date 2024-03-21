import json
from pathlib import Path


def load_all_target_to_english_dictionaries():
    dictionaries = {}

    lexilogos_folder = Path("resources/lexilogos")
    lexilogos_files = lexilogos_folder.glob("*")

    for file in lexilogos_files:
        language = file.stem

        if not file.is_file():
            # Making sure it is actually a file
            continue

        with open(file, "r") as f:
            data = json.load(f)

        custom_target_to_english_dictionaries = data["dictionaries"][
            "custom_target_to_english"
        ]

        target_to_english_dictionaries = data["dictionaries"]["target_to_english"]

        # Simply merge all the dictionaries
        dictionaries[language] = custom_target_to_english_dictionaries
        dictionaries[language].update(target_to_english_dictionaries)

    return dictionaries
