import os, json


def load_all_tl_to_english_dictionaries():
    dictionaries = {}

    lexilogos_folder = "resources/lexilogos"
    lexilogos_files = os.listdir(lexilogos_folder)

    for file in lexilogos_files:
        language = os.path.splitext(file)[0]

        filepath = os.path.join(lexilogos_folder, file)

        if not os.path.isfile(filepath):
            # Making sure it is actually a file
            continue

        with open(filepath, "r") as f:
            data = json.load(f)

        language_to_eng_dictionaries = data["language_to_eng"]

        dictionaries[language] = language_to_eng_dictionaries

    return dictionaries
