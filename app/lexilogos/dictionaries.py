import os, json


def load_dictionaries():
    languages_and_their_dictionaries = {}

    lexilogos_data = "./LangAnki/UI/Lexilogos/json_ready_march_23/english_data"
    lexilogos_files = os.listdir(lexilogos_data)

    for file in lexilogos_files:
        language = os.path.splitext(file)[0]

        filepath = os.path.join(lexilogos_data, file)

        with open(filepath, "r") as f:
            data = json.load(f)

        language_to_eng_dictionaries = data["language_to_eng"]

        languages_and_their_dictionaries[language] = language_to_eng_dictionaries

    return languages_and_their_dictionaries