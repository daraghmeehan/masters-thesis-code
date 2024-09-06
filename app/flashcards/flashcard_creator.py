import os
import time  # To timestamp created csvs
from typing import Dict, List

import pandas as pd  # For easy manipulation and exporting of flashcard data
from pathlib import Path  # For writing flashcards to the "Flashcards" folder


class FlashcardCreator:
    """
    A class to manage the creation and manipulation of flashcard decks.

    Attributes:
        deck_name (str): The name of the flashcard deck.
        flashcard_fields (List[str]): The names of the fields of the flashcards.
        file_path (Path): The path to the CSV file where flashcards are stored.
    """

    def __init__(self, deck_name: str, fields: List[str], output_folder: str) -> None:
        """
        Initialize the FlashcardCreator with a deck name and flashcard fields.

        Parameters:
        deck_name (str): The name of the flashcard deck.
        fields (List[str]): The list of field names for the flashcards.
        output_folder (str): The folder where flashcards should be saved.
        """
        self.deck_name = deck_name
        self.flashcard_fields = fields
        self.file_path = self.create_flashcard_deck(fields, output_folder)

    def create_flashcard_deck(self, fields: List[str], output_folder: str) -> Path:
        """
        Create a new flashcard deck as a CSV file with the specified fields.

        Parameters:
        fields (List[str]): The list of field names.
        output_folder (str): The folder where flashcards should be saved.

        Returns:
        Path: The path to the created CSV file where flashcards are saved.
        """
        timestamp = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
        file_name = f"{self.deck_name} - {timestamp}.csv"
        file_path = Path(output_folder) / file_name
        file_path.parent.mkdir(
            exist_ok=True
        )  # Create the flashcard directory if it doesn't exist

        # Create the file if it doesn't exist
        if not file_path.exists():
            pd.DataFrame(columns=fields).to_csv(file_path, index=False, header=False)

        return file_path

    def number_of_flashcards_created(self) -> int:
        """
        Count the number of flashcards in the CSV file.

        Returns:
        int: The number of flashcards in the file. Returns 0 if the file does not exist.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return sum(1 for row in file)
        except FileNotFoundError:
            return 0  # Return 0 if the file doesn't exist

    def add_flashcard(self, card_as_dict: Dict[str, str]) -> None:
        """
        Add a new flashcard to the CSV file.

        Parameters:
        card_as_dict (Dict[str, str]): A dictionary representing the flashcard - keys are field names, entries are the field data.
        """
        assert (
            list(card_as_dict.keys()) == self.flashcard_fields
        ), "Flashcard keys do not match the required fields."
        assert not all(
            [field == "" for field in card_as_dict.values()]
        ), "All field values are empty."

        new_card = pd.DataFrame([card_as_dict])
        new_card.to_csv(self.file_path, mode="a", header=False, index=False)

    def retrieve_all_flashcards_created(self):
        """
        Retrieve all flashcards from the CSV file.

        Returns:
        pd.DataFrame: A DataFrame containing all flashcards. Returns an empty DataFrame if no flashcards are found or if an error occurs.
        """
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
        """
        Delete the flashcard deck file.

        Returns:
        bool: True if the file was successfully deleted, False otherwise.
        """
        try:
            file_path = Path(self.file_path)
            # Check if the file exists
            if file_path.exists():
                file_path.unlink()  # Delete the file
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
