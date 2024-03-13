import os, json


def load_all_target_to_english_dictionaries():
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

        custom_target_to_english_dictionaries = data["dictionaries"][
            "custom_target_to_english"
        ]

        target_to_english_dictionaries = data["dictionaries"]["target_to_english"]

        # Simply merge all the dictionaries
        dictionaries[language] = custom_target_to_english_dictionaries
        dictionaries[language].update(target_to_english_dictionaries)

    return dictionaries
