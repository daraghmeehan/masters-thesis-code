import os
import time  # To timestamp created csvs

import pandas as pd  # to manage flashcard data - easy manipulation and exporting
from pathlib import Path  # for writing flashcards to "Flashcards" folder


class FlashcardCreator:
    def __init__(self, deck_name, fields) -> None:
        self.deck_name = deck_name
        self.flashcard_fields = fields
        self.file_path = self.create_flashcard_deck(fields)

    def create_flashcard_deck(self, fields):
        timestamp = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
        file_name = f"{self.deck_name} - {timestamp}"
        file_path = Path(f"../media/flashcards/new_cards/{file_name}.csv")
        file_path.parent.mkdir(
            exist_ok=True
        )  # Making the "Flashcard" directory if we don't already have it

        # Create the file with headers if it doesn't exist
        if not file_path.is_file():
            pd.DataFrame(columns=fields).to_csv(file_path, index=False, header=False)

        return file_path

    def number_of_flashcards_created(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return sum(1 for row in file)
        except FileNotFoundError:
            return 0  # Return 0 if the file doesn't exist

    def add_flashcard(self, card_as_dict):
        # Below is handling even if not all keys are present (it's more general)
        # # Ensure that all keys are valid
        # assert all(field in self.flashcard_fields for field in card_as_dict.keys())
        # # Ensure that at least one value is not empty
        # assert any(card_as_dict.values())

        # # Create a new dictionary with missing fields filled in as empty strings
        # new_card_dict = {field: card_as_dict.get(field, "") for field in self.flashcard_fields}
        # # Convert the dictionary to a DataFrame
        # new_card = pd.DataFrame([new_card_dict])

        # print(f"keys: {list(card_as_dict.keys())}\nfields: {self.flashcard_fields}")
        assert list(card_as_dict.keys()) == self.flashcard_fields
        assert not all([field == "" for field in card_as_dict.values()])

        new_card = pd.DataFrame([card_as_dict])
        new_card.to_csv(self.file_path, mode="a", header=False, index=False)

    def retrieve_all_flashcards_created(self):
        try:
            # Read the CSV file into a DataFrame
            flashcards_df = pd.read_csv(self.file_path, encoding="utf-8")
            return flashcards_df
        except FileNotFoundError:
            # Handle the case where no flashcards have been created yet
            print(f"No flashcards found in {self.file_path}.")
            return pd.DataFrame()  # Return an empty DataFrame
        except Exception as e:
            # Handle other potential exceptions
            print(f"An error occurred while retrieving flashcards: {e}")
            return pd.DataFrame()

    def delete_deck(self):
        try:
            # Check if the file exists
            if os.path.exists(self.file_path):
                os.remove(self.file_path)  # Delete the file
                print(f"Deleted flashcard deck: {self.file_path}")
                return True
            else:
                print(f"Flashcard deck not found: {self.file_path}")
                return False
        except Exception as e:
            print(
                f"An error occurred while deleting the flashcard deck {self.deck_name}: {e}"
            )
            return False
