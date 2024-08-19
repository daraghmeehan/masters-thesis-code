import json
from typing import Optional, Dict, Any


def read_flashcard_templates(flashcard_templates_path: str) -> Optional[Dict[str, Any]]:
    """
    Reads flashcard templates from a JSON file.

    Parameters:
    flashcard_templates_path (str): The path to the JSON file containing flashcard templates.

    Returns:
    Optional[Dict[str, Any]]: A dictionary containing the flashcard templates if the file is read successfully,
                              or None if an error occurs (e.g., file not found, invalid JSON).
    """
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
