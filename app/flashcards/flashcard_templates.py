import json


def read_flashcard_templates(flashcard_templates_path):
    try:
        with open(flashcard_templates_path, "r", encoding="utf-8") as file:
            flashcard_templates = json.load(file)
            return flashcard_templates
    except FileNotFoundError:
        print(f"The file {flashcard_templates_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"The file {flashcard_templates_path} contains invalid JSON.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
