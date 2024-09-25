## Standard library imports
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime


## Third-party imports
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QShortcut
from PyQt5.QtGui import QKeySequence

import webbrowser  # For opening links (dictionary searches) in web browser
import pyperclip  # For clipboard operations


## Local imports
from media_exporter.media_exporter import MediaExporter

from model.model import AVIModel

# Translator/Dictionaries
from deep_l.translator import load_translator
from lexilogos.dictionaries import load_all_target_to_english_dictionaries

# UI imports
from ui.startup_dialog import StartupDialog
from ui.media_exporter_window import MediaExporterWindow
from ui.view import MainWindow
from ui.flashcard_workspace import ScreenshotViewer, AudioViewer
from ui.sentence_bin import SentenceBin
from ui.study_materials import SegmentHeader, SavedSentenceEntry

# Flashcard creation functionality
from flashcards.flashcard_templates import read_flashcard_templates
from flashcards.flashcard_creator import FlashcardCreator

from avi_utils.screenshot_extractor import ScreenshotExtractor
from avi_utils.audio_player import AudioPlayer
from avi_utils.audio_extractor import AudioExtractor

# Shortcuts for trying different startup options
from startup_options import (
    text_mode_options,
    cuentame_startup_options,
    peppa_startup_options,
    gg_startup_options,
)

# Two below to make scaling bigger on small high-res screens
if hasattr(Qt, "AA_EnableHighDpiScaling"):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, "AA_UseHighDpiPixmaps"):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class Controller:
    """
    The Controller class orchestrates the entire application workflow, serving as the central
    hub that coordinates the setup, execution, and teardown of various components.

    It manages the following key processes:
    - Initialisation of language reference tools, flashcard creators, and user interfaces.
    - Running the startup dialog to parse user options, such as selected languages and mode.
    - Setting up audiovisual processing tools for AVI Mode, including media extractors, audio players, and UI components.
    - Executing the main application loop, handling event processing, and coordinating the interaction between the model and view.
    - Performing cleanup operations, such as exporting flashcards and deleting temporary files, after execution.

    It also manages the creation of condensed audio practice files if using the Media Export Mode.

    This class is designed to be the entry point for the application, ensuring that all components work together seamlessly.
    """

    def __init__(self) -> None:
        pass

    def run(self) -> None:
        """
        Runs the main application process.

        This method orchestrates the setup of language reference tools, initializes
        the user interface, and handles the application's main loop in the various Modes.
        It also manages the setup of media extractors for audiovisual input when working
        with audiovisual input and performs cleanup operations after execution.

        The process includes:
        - Loading the translator and dictionaries (the language reference tools).
        - Setting up the flashcard creators.
        - Running the startup dialog and parsing the selected options.
        - Initializing the model and UI based on the chosen mode.
        - Executing the application's event loop.
        - Exporting flashcards created and cleaning temporary files.
        """
        # TODO: In future, allow for loading more dictionaries, e.g. with "dictionaries.load_all_target..." instead
        self.target_to_english_dictionaries = load_all_target_to_english_dictionaries()

        # TODO: Perhaps make this a different object in future
        # Run and parse the startup dialog, where the user chooses the languages/media they wish to study
        # startup_options = self.run_startup_dialog()

        # For quicker testing
        # startup_options = cuentame_startup_options
        startup_options = peppa_startup_options
        # startup_options = gg_startup_options
        # startup_options = text_mode_options

        self.parse_startup_options(startup_options)

        if self.mode == "Export Media":
            # TODO: Need to be convert all with paths as strings to Path objects!
            # TODO: Also should refactor this.
            self.temporary_audio_folder = Path("../temp/audio").resolve()
            self.avi_practice_audio_folder = Path("../media/audio").resolve()

            # Load the media exporter UI
            self.app = QApplication([])
            media_exporter_window = MediaExporterWindow()

            # Create an instance of the backend media exporter
            media_exporter = MediaExporter(
                temporary_audio_folder=self.temporary_audio_folder,
                avi_practice_audio_folder=self.avi_practice_audio_folder,
            )

            # Connect the UI signal to the backend export function
            media_exporter_window.export_signal.connect(media_exporter.export_media)

            try:
                # Run the application window
                media_exporter_window.show()
                self.app.exec_()

            finally:
                # Clean temporary files after the operation
                self.clean_temporary_files()

            return

        # Otherwise, set up for study in Text/AVI Mode :)
        self.translator = load_translator()

        # TODO: Probably refactor this.
        ## Get ready to make flashcards
        # Read flashcard templates
        flashcard_templates_path = "resources/flashcards/flashcard_templates.json"
        flashcard_template = self.load_flashcard_template(flashcard_templates_path)
        self.parse_flashcard_template(flashcard_template)

        # Set up flashcard creators
        flashcard_output_folder = "../media/flashcards/new_cards"
        self.flashcard_creators = self.set_up_flashcard_creators(
            flashcard_output_folder
        )

        # Setup AVI Mode
        if self.mode == "AVI":
            self.temporary_audio_folder = "../temp/audio"
            self.flashcard_audio_folder = "../media/flashcards/flashcard_audio"
            self.flashcard_image_folder = "../media/flashcards/flashcard_images"

            # Set up the media extractors
            self.set_up_audio_extractor()
            self.set_up_screenshot_extractor()

            # To play and export subtitle audio
            self.audio_player = AudioPlayer()

        try:
            # Set up the model and the view
            self.set_up_model()
            self.set_up_ui()

            # Show the UI and run the event loop
            self.ui.show()
            self.app.exec_()
        finally:
            # Clean up our work
            self.delete_empty_decks()
            if self.mode == "AVI":
                self.clean_temporary_files()
            pass

    def run_startup_dialog(self) -> dict:
        """
        Runs the startup dialog to allow the user to select their startup options.

        Returns:
            dict: A dictionary containing the selected startup options.

        Exits the program if the dialog is rejected.
        """
        startup_app = QApplication([])
        startup_dialog = StartupDialog(self.target_to_english_dictionaries)
        if startup_dialog.exec_() == QDialog.Accepted:
            startup_options = startup_dialog.get_options()
            return startup_options
        exit()  # If dialog is rejected

    def parse_startup_options(self, startup_options: dict) -> None:
        """Parses the provided startup options and configures instance variables accordingly."""
        self.mode = startup_options["Mode"]
        if self.mode == "Export Media":
            return
        self.source_language = startup_options["Source Language"]
        self.target_languages = startup_options["Target Languages"]
        self.languages = [self.source_language] + self.target_languages
        self.dictionaries = startup_options["Dictionaries"]
        if self.mode == "AVI":
            self.video_file = startup_options["Video File"]
            self.audio_tracks = startup_options["Audio Tracks"]
            self.subtitle_files = startup_options["Subtitle Files"]

    def load_flashcard_template(self, flashcard_templates_path: str) -> dict:
        """
        Loads the flashcard templates from a JSON file.

        Args:
            flashcard_templates_path (str): The file path to the JSON flashcard templates.

        Returns:
            dict: The loaded flashcard template as a dictionary.
        """
        flashcard_templates = read_flashcard_templates(flashcard_templates_path)
        flashcard_template = flashcard_templates["languages_template"]
        return flashcard_template

    def parse_flashcard_template(self, flashcard_template: dict) -> None:
        """
        Parses the flashcard template to set up instance variables for flashcard fields, required fields, and decks.

        Args:
            flashcard_template (dict): A dictionary containing flashcard template data.
        """
        self.flashcard_fields = flashcard_template["fields"]
        self.required_fields = flashcard_template["required_fields"]
        self.decks = flashcard_template["decks"]

    def set_up_flashcard_creators(self, flashcard_output_folder: str) -> dict:
        """
        Sets up flashcard creators for each deck based on the parsed flashcard template.

        Args:
            flashcard_output_folder (str): The directory where the flashcards will be saved.

        Returns:
            dict: A dictionary mapping deck names to their corresponding FlashcardCreator instances.
        """
        flashcard_creators = {}

        flashcard_field_names = list(self.flashcard_fields.keys())
        if "Tags" in flashcard_field_names:
            # TODO: Implement handling flashcard tags at some stage.
            flashcard_field_names.remove("Tags")
        for deck in self.decks:
            flashcard_creator = FlashcardCreator(
                deck_name=f"({self.mode}) Languages {deck}",
                fields=flashcard_field_names,
                output_folder=flashcard_output_folder,
            )
            flashcard_creators[deck] = flashcard_creator

        return flashcard_creators

    def set_up_screenshot_extractor(self) -> None:
        """
        Sets up the screenshot extractor for extracting screenshots from the video file.

        This method initialises the `ScreenshotExtractor` with the path to the video file.
        """
        self.screenshot_extractor = ScreenshotExtractor(str(self.video_file))

    def set_up_audio_extractor(self) -> None:
        """
        Sets up the audio extractor for extracting audio tracks from the video file.

        This method initialises the `AudioExtractor` with a temporary folder for audio files
        and extracts all specified language tracks from the video file.
        """
        self.audio_extractor = AudioExtractor(Path(self.temporary_audio_folder))
        self.audio_extractor.extract_all_language_tracks(
            Path(self.video_file), self.audio_tracks
        )  # Extract the audio tracks of the video file

    def set_up_model(self) -> None:
        """
        Sets up the model based on the current mode.

        This method initialises different models depending on the Mode:
        - For Text mode, no action is taken.
        - For AVI mode, it builds an `AVIModel` with the subtitle files.
        """
        if self.mode == "Text":
            pass
        elif self.mode == "AVI":
            self.model = AVIModel(self.subtitle_files)

    def set_up_ui(self) -> None:
        """
        Sets up the user interface for the application based on the current mode.

        This method initializes the QApplication instance, sets the main window title,
        and sets up various UI components, including workspaces, shortcuts, and signals.
        """
        self.app = QApplication([])

        if self.mode == "AVI":
            main_window_title = (
                f"{self.video_file} - {', '.join(tl for tl in self.target_languages)}"
            )
        else:
            main_window_title = self.target_languages[0]

        # Set up the view
        self.ui = MainWindow(
            window_title=main_window_title, mode=self.mode, languages=self.languages
        )

        # Set up key widgets of the UI
        self.set_up_flashcard_workspace()
        self.set_up_translation_workspace()
        self.set_up_dictionary_lookup()
        self.set_up_study_materials()

        # Set up UI workflow
        self.set_up_shortcuts()
        self.set_up_all_enter_key_signals()

    def set_up_flashcard_workspace(self) -> None:
        """
        Configures the Flashcard Workspace within the UI.

        This method sets up the dropdown menu, adds fields, configures buttons, and connects
        signals to their respective slots based on the current mode.
        """
        self.ui.flashcard_workspace.deck_dropdown.addItems(self.decks)
        self.ui.flashcard_workspace.deck_dropdown.setCurrentIndex(1)

        for field_name, field_info in self.flashcard_fields.items():
            self.ui.flashcard_workspace.add_field(field_name, field_info)

        self.ui.flashcard_workspace.fields["Question Language"].addItems(self.languages)
        self.ui.flashcard_workspace.fields["Answer Language"].addItems(self.languages)

        self.ui.flashcard_workspace.translate_question_text_button.clicked.connect(
            self.translate_question_text
        )

        if self.mode == "AVI":
            self.ui.flashcard_workspace.fields["Audio"].play_requested.connect(
                self.play_flashcard_audio
            )
            self.ui.flashcard_workspace.fields["Audio"].stop_requested.connect(
                self.stop_flashcard_audio
            )
            self.ui.flashcard_workspace.fields["Audio"].change_audio_time.connect(
                self.change_flashcard_audio_time
            )

        self.ui.flashcard_workspace.add_button.clicked.connect(self.add_flashcard)
        self.ui.flashcard_workspace.edit_previous_button.clicked.connect(
            self.edit_previous_flashcards
        )

    def translate_question_text(self) -> None:
        """
        Translates the text in the "Question Text" field from the source language to the target language
        and updates the "Answer Text" field with the translated text.

        The translation only occurs if the source and target languages are different and the question text is not empty.
        """
        question_language = self.ui.flashcard_workspace.fields[
            "Question Language"
        ].currentText()
        answer_language = self.ui.flashcard_workspace.fields[
            "Answer Language"
        ].currentText()
        question_text = (
            self.ui.flashcard_workspace.fields["Question Text"].toPlainText().strip()
        )

        if question_language == answer_language or question_text == "":
            return

        answer_text = self.translator.translate_text(
            texts=[question_text],
            source_lang=question_language,
            target_lang=answer_language,
        )[0]

        self.ui.flashcard_workspace.fields["Answer Text"].setText(answer_text)

    def play_flashcard_audio(self, audio_path: str) -> None:
        """
        Plays the audio file specified by `audio_path`.

        Stops any currently playing audio, updates the audio player if necessary,
        and starts playback of the new audio file.

        Args:
            audio_path (str): The path to the audio file to be played.
        """
        self.audio_player.stop()

        if audio_path != self.audio_player.get_audio_path():
            self.audio_player.reset_player()
            self.audio_player.update_audio(audio_path)

        self.audio_player.play()

    def stop_flashcard_audio(self) -> None:
        """
        Stops the currently playing flashcard audio.
        """
        self.audio_player.stop()

    def change_flashcard_audio_time(
        self, start_or_end_time: str, adjustment: float
    ) -> None:
        """
        Adjusts the start or end time of the flashcard audio file.

        This method reextracts the flashcard audio file with the new time adjustments.

        Args:
            start_or_end_time (str): Specifies whether to adjust the start or end time ("start" or "end").
            adjustment (float): The amount of time to adjust by, in seconds.
        """
        # TODO: Reextract flashcard audio file with different start/end time
        pass

    def add_flashcard(self) -> None:
        """
        Creates a new flashcard from the current data in the Flashcard Workspace and adds it to the selected deck.

        The method gathers data from various fields, ensures that all required fields are filled,
        and then adds the flashcard to the appropriate deck. Media files are saved and referenced accordingly.

        The flashcard is saved to the deck selected in the Flashcard Workspace's dropdown menu.
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")  # For uniquely naming files

        flashcard = {}
        for field_name, field_info in self.flashcard_fields.items():
            if field_info["type"] == "Media":
                if self.mode == "AVI":
                    media_path = self.save_card_media(field_name, timestamp)
                    field_data = media_path
                    if field_name == "Audio":
                        # Ensuring the audio file reference is correctly formatted to work in Anki
                        field_data = (
                            "[sound:" + field_data + "]" if media_path else ""
                        )  #!! Make sure this returns [sound etc] if has audio, and blank if not :)
                else:
                    field_data = ""
            elif field_name == "Tags":
                # TODO: Tags need to be implemented in future
                continue
            else:
                field_data = self.ui.flashcard_workspace.extract_field_data(field_name)
            flashcard[field_name] = field_data

        # Ensuring all our required fields have some data
        for required_field in self.required_fields:
            if flashcard[required_field] == "":
                # TODO: If required fields blank, still might have saved card media that needs to be deleted.
                print(
                    f"{required_field} is a required field but is blank! Rejecting card..."
                )
                return

        # Retrieving the chosen deck
        deck = self.ui.flashcard_workspace.deck_dropdown.currentText()

        # Adding our card to the appropriate deck
        self.flashcard_creators[deck].add_flashcard(flashcard)

        # Resetting the Flashcard Workspace
        self.ui.flashcard_workspace.reset_flashcard_fields()

    def save_card_media(self, field_name: str, timestamp: str) -> str:
        """
        Saves the media associated with the given field and returns the filename.

        The method handles screenshots and audio, saving them to the appropriate folders and generating a filename
        based on the given timestamp (to uniquely name files).

        Args:
            field_name (str): The name of the field containing the media.
            timestamp (str): A unique timestamp to ensure filenames are unique.

        Returns:
            str: The filename of the saved media.
        """
        filename = ""  # Media flashcard fields must point to the filename
        media_widget = self.ui.flashcard_workspace.fields[field_name]

        if (
            isinstance(media_widget, ScreenshotViewer)
            and media_widget.has_screenshots()
        ):
            file_extension = ".jpg"
            # Note: "_languages_" is used to be able to find created media easily in Anki's media folder
            filename = "_languages_" + timestamp + file_extension
            path = Path(self.flashcard_image_folder) / filename
            media_widget.save_screenshot(path)

        elif isinstance(media_widget, AudioViewer) and media_widget.has_audio():
            audio_path = self.ui.flashcard_workspace.fields["Audio"].get_audio_path()

            if self.audio_player.get_audio_path != audio_path:
                # In case we have played other media, e.g. from parallel text, in the meantime
                self.audio_player.update_audio(audio_path)

            file_extension = ".mp3"
            # "_languages_" is code to be able to find language card pictures easily in Anki media folder
            filename = "_languages_" + timestamp + file_extension
            path = Path(self.flashcard_audio_folder) / filename
            self.audio_player.save_audio(path)

        return filename

    def edit_previous_flashcards(self) -> None:
        # TODO: Implement ability to edit previously made flashcards
        pass

    def set_up_translation_workspace(self) -> None:
        """
        Sets up the Translation Workspace UI components, including connecting buttons to their respective functions.

        This method configures the Translation Workspace with the available languages and sets up the event
        handlers for translating text and creating flashcards from the workspace.
        """
        # Set the initial languages
        self.ui.translation_workspace.set_languages(
            languages=self.languages,
            source_language=self.target_languages[0],
            target_language=self.source_language,
        )

        # Connect the buttons
        self.ui.translation_workspace.translate_button.clicked.connect(
            self.translate_from_workspace
        )
        self.ui.translation_workspace.flashcard_button.clicked.connect(
            self.make_flashcard_from_workspace
        )

    def translate_from_workspace(self) -> None:
        """
        Translates text from the source language to the target language using the translator.

        Retrieves the source language text from the translation workspace, performs the translation,
        and sets the translated text in the target language field. If the source and target languages
        are the same or if the source text is empty, no action is taken.

        Exceptions during translation are handled, setting the translation to an empty string in case of failure.
        """
        source_language_text = self.ui.translation_workspace.get_source_language_text()
        if source_language_text == "":
            return

        source_language = self.ui.translation_workspace.get_source_language()
        target_language = self.ui.translation_workspace.get_target_language()

        if source_language == target_language:
            return  # Don't do anything if translating between same language

        try:
            # In translation the source language is translated to the target language
            translation = self.translator.translate_text(
                texts=[source_language_text],
                source_lang=source_language,
                target_lang=target_language,
            )[0]
        except:
            translation = ""

        self.ui.translation_workspace.set_target_language_text(translation)

    def make_flashcard_from_workspace(self) -> None:
        """
        Creates a flashcard from the current text in the translation workspace.

        Retrieves the source and target language texts, populates the flashcard workspace with these texts,
        and sets the language fields accordingly. Clears the translation workspace after creating the flashcard.

        If either the source or target text is empty, no action is taken.
        """
        source_language_text = self.ui.translation_workspace.get_source_language_text()
        target_language_text = self.ui.translation_workspace.get_target_language_text()

        if source_language_text == "" or target_language_text == "":
            return

        source_language = self.ui.translation_workspace.get_source_language()
        target_language = self.ui.translation_workspace.get_target_language()

        self.ui.flashcard_workspace.reset_flashcard_fields()

        self.ui.flashcard_workspace.fields["Question Text"].setText(
            source_language_text
        )
        self.ui.flashcard_workspace.fields["Answer Text"].setText(target_language_text)

        self.ui.flashcard_workspace.fields["Question Language"].setCurrentText(
            source_language
        )
        self.ui.flashcard_workspace.fields["Answer Language"].setCurrentText(
            target_language
        )

        self.ui.translation_workspace.clear_workspace()

    def set_up_dictionary_lookup(self) -> None:
        """
        Sets up the Dictionary Lookup UI components and connects buttons to their respective functions.

        Configures the Dictionary Lookup interface with available dictionaries, and sets up event handlers
        for searching words and looking up words in specific dictionaries.
        """
        self.ui.dictionary_lookup.set_up_dictionaries(self.dictionaries)
        self.ui.dictionary_lookup.search_button.clicked.connect(self.look_up_word)
        self.ui.dictionary_lookup.search_requested.connect(
            self.look_up_word_in_one_dictionary
        )

    def look_up_word(self) -> None:
        """
        Opens a web browser to search for the specified word in selected dictionaries.

        Retrieves the word to search, determines the selected language and dictionaries, constructs the
        search URL, and opens the URL in a web browser. If the search bar is empty, no action is taken.
        """
        word = self.ui.dictionary_lookup.get_text()

        if word == "":
            return

        language = self.ui.dictionary_lookup.get_language()
        dictionaries_to_search = self.ui.dictionary_lookup.get_selected_dictionaries(
            language
        )

        for dictionary in dictionaries_to_search:
            formatting = self.target_to_english_dictionaries[language][dictionary][
                "url"
            ]
            search_address = formatting[0] + word + formatting[1]
            webbrowser.open(
                search_address,  # autoraise=False
            )
            # TODO: Find way or of setting focus on the opened window

    def look_up_word_in_one_dictionary(self, language: str, dictionary: str) -> None:
        """
        Opens a web browser to search for the specified word in a single dictionary.

        Constructs the search URL based on the specified language and dictionary, then opens the URL
        in a web browser. If the search bar is empty, no action is taken.

        Args:
            language (str): The language for which the word lookup is to be performed.
            dictionary (str): The specific dictionary to use for the lookup.
        """
        word = self.ui.dictionary_lookup.get_text()

        if word == "":
            return

        formatting = self.target_to_english_dictionaries[language][dictionary]["url"]
        search_address = formatting[0] + word + formatting[1]
        webbrowser.open(
            search_address,  # autoraise=False
        )

    def set_up_study_materials(self) -> None:
        """
        Configures the Study Materials based on the selected mode.

        Sets up the Study Materials UI and processes based on whether the mode is "AVI" or "Text".
        For "AVI" mode, it sets up subtitle workspaces and initial subtitle alignment.
        For "Text" mode, it sets up saved sentences.
        """
        if self.mode == "Text":
            self.set_up_saved_sentences()
        elif self.mode == "AVI":
            # import sys
            # sys.argv.append(self.model) ## For testing

            self.set_up_subtitle_workspace()

            # TODO: Implement choosing segment parameters while setting up the application, and changing it while the application is running.
            # self.model.create_segments(maximum_seconds_between_segments=3)

            # Building the alignment in the Model
            initial_alignment = self.model.get_alignment()
            # Setting the alignment in the View
            self.set_subtitle_alignment(initial_alignment)

    def set_up_subtitle_workspace(self) -> None:
        """
        Configures the Subtitle Workspace with the available subtitles and audio tracks.

        Passes the languages that have subtitles and audio tracks to the Subtitle Workspace.
        Connects signals for creating flashcards and playing subtitle audio to their respective slots.
        """
        self.ui.study_materials.subtitle_workspace.languages_with_subtitles = [
            language
            for language, subtitle_file in self.subtitle_files.items()
            if language != "Reference" and subtitle_file
        ]
        self.ui.study_materials.subtitle_workspace.languages_with_audio_tracks = [
            language
            for language, audio_track in self.audio_tracks.items()
            if audio_track != "None"
        ]
        self.ui.study_materials.subtitle_workspace.flashcard_requested_signal.connect(
            self.make_flashcard_from_subtitle
        )
        self.ui.study_materials.subtitle_workspace.listen_requested_signal.connect(
            self.play_subtitle_audio
        )

    def make_flashcard_from_subtitle(self, language: str, index: int) -> None:
        """
        Creates a flashcard from the specified subtitle.

        Retrieves the subtitle based on the provided language and index, extracts screenshots and the audio
        segment, and populates the flashcard workspace with the subtitle text, language, pictures, and audio.

        Args:
            language (str): The language of the subtitle.
            index (int): The index of the subtitle in the provided language.
        """
        # TODO: Perhaps rename index/indices to number/numbers.
        subtitle = self.model.get_subtitle(language, index)

        start_time, end_time, text = (
            subtitle.start_time,
            subtitle.end_time,
            subtitle.text,
        )

        screenshots = self.screenshot_extractor.extract_screenshots(
            start_time, end_time
        )

        self.ui.flashcard_workspace.reset_flashcard_fields()

        self.ui.flashcard_workspace.fields["Question Text"].setText(text)
        self.ui.flashcard_workspace.fields["Question Language"].setCurrentText(language)
        self.ui.flashcard_workspace.fields["Picture"].update_screenshots(screenshots)

        if self.audio_tracks[language] != "None":
            self.audio_player.stop()
            self.audio_player.reset_player()  # Otherwise we can't extract the segment if the last audio played was also for a flashcard
            audio_segment_path = self.audio_extractor.extract_segment(
                language, start_time, end_time, segment_name="flashcard_segment"
            )
            self.ui.flashcard_workspace.fields["Audio"].update_audio(
                str(audio_segment_path)
            )
            self.audio_player.update_audio(str(audio_segment_path))

    def play_subtitle_audio(self, language: str, index: int) -> None:
        """
        Plays the audio segment associated with a subtitle.

        Stops and resets the audio player, extracts the audio segment based on the subtitle's start and end times,
        and plays the extracted audio segment.

        Args:
            language (str): The language of the subtitle.
            index (int): The index of the subtitle in the specified language.
        """
        if self.audio_tracks[language] == "None":
            return

        self.audio_player.stop()
        self.audio_player.reset_player()

        subtitle = self.model.get_subtitle(language, index)

        # TODO: Allow for a default padding value to add to start/end times.
        audio_segment_path = self.audio_extractor.extract_segment(
            language,
            subtitle.start_time,
            subtitle.end_time,
            segment_name="subtitle_segment",
        )

        self.audio_player.update_audio(str(audio_segment_path))
        self.audio_player.play()

    # TODO: Refactor this and above method.
    def play_segment_audio(
        self, start_time: datetime, end_time: datetime, language: str
    ) -> None:
        """
        Plays an audio segment based on given start and end times and chosen language track.

        Stops and resets the audio player, extracts the audio segment from the specified start and end times
        for the given language track, and plays the extracted audio segment.

        Args:
            start_time (datetime): The start time of the audio segment.
            end_time (datetime): The end time of the audio segment.
            language (str): The language of the audio track.
        """
        if self.audio_tracks[language] == "None":
            return

        self.audio_player.stop()
        self.audio_player.reset_player()

        audio_segment_path = self.audio_extractor.extract_segment(
            language, start_time, end_time, segment_name="full_segment"
        )

        self.audio_player.update_audio(str(audio_segment_path))
        self.audio_player.play()

    # TODO: Is this in the right place?
    def set_subtitle_alignment(self, alignment: List[Dict]) -> None:
        """
        Sets the subtitle alignment and updates the UI workspace accordingly.

        Args:
            alignment (List[Dict]): A list of alignment entries containing timings, subtitle indices, and segments.
        """
        self.ui.study_materials.subtitle_workspace.clear_workspace()

        num_segments = alignment[-1]["segment"]

        current_segment = 1
        segment_start_time, segment_end_time = alignment[0]["timings"]

        segment_header = self.ui.study_materials.subtitle_workspace.add_segment_header(
            current_segment, num_segments
        )

        # Loop through each reference subtitle
        for idx, entry in enumerate(alignment):
            if entry["segment"] != current_segment:
                ## Start a new segment

                # First finalise the previous segment
                self._finalise_segment(
                    segment_header, segment_start_time, segment_end_time
                )

                # Track new segment start time
                current_segment = entry["segment"]
                segment_start_time, segment_end_time = entry["timings"]

                # Add segment header for the new segment
                segment_header = (
                    self.ui.study_materials.subtitle_workspace.add_segment_header(
                        current_segment, num_segments
                    )
                )
            else:
                segment_end_time = entry["timings"][
                    1
                ]  # Otherwise keep extending current segment end time

            if idx == len(alignment) - 1:
                # If handling last entry. It's ok if we finalise the segment again in case the last entry is also a separate segment.
                self._finalise_segment(
                    segment_header, segment_start_time, segment_end_time
                )

            # Gathering all subtitle indices and texts of the current entry to add them to the Subtitle Workspace
            subtitles = self._gather_subtitles(entry)
            self.ui.study_materials.subtitle_workspace.add_entry(subtitles)

    def _finalise_segment(
        self,
        segment_header: SegmentHeader,
        segment_start_time: float,
        segment_end_time: float,
    ) -> None:
        """
        Finalises a segment by adding timings to the segment header and connecting the signal.

        Args:
            segment_header (SegmentHeader): The segment header in the UI to be finalised.
            segment_start_time (float): The start time of the segment.
            segment_end_time (float): The end time of the segment.
        """
        segment_header.add_timings(segment_start_time, segment_end_time)
        segment_header.listen_requested_signal.connect(self.play_segment_audio)

    # TODO: Perhaps refactor this or place elsewhere.
    def _gather_subtitles(self, entry: Dict) -> Dict[str, Dict[str, List]]:
        """
        Gathers subtitle indices and texts for each language based on the alignment entry.

        Args:
            entry (Dict): An alignment entry containing subtitle indices for each language.

        Returns:
            Dict[str, Dict[str, List]]: A dictionary with languages as keys, and each language contains a dictionary
                                        with 'indices' and 'texts' as keys, holding lists of subtitle indices and texts.
        """
        subtitles = {
            language: {"indices": [], "texts": []} for language in self.model.languages
        }

        for language in self.model.languages:
            all_subtitle_indices = entry["subtitle_indices"][language]
            if all_subtitle_indices == []:
                continue

            # Using the indices to gather the appropriate subtitle text to display
            all_subtitle_texts = []
            for subtitle_index in all_subtitle_indices:
                subtitle_text = self.model.get_subtitle(language, subtitle_index).text
                all_subtitle_texts.append(subtitle_text)

            subtitles[language]["indices"] = all_subtitle_indices
            subtitles[language]["texts"] = all_subtitle_texts

        return subtitles

    def set_up_saved_sentences(self) -> None:
        """
        Sets up the Saved Sentences window (when using Text Mode) by setting up the Sentence Bin and connecting signals to their corresponding methods.
        """
        self.set_up_sentence_bin()
        self.ui.study_materials.saved_sentences.add_new_from_clipboard_button.clicked.connect(
            self.add_entry_from_clipboard
        )

        self.ui.study_materials.saved_sentences.translate_entry_signal.connect(
            self.translate_entry
        )
        self.ui.study_materials.saved_sentences.make_flashcard_from_entry_signal.connect(
            self.make_flashcard_from_entry
        )

        self.ui.study_materials.saved_sentences.translate_all_button.clicked.connect(
            self.translate_all_entries
        )

    def translate_entry(self, entry_widget: SavedSentenceEntry) -> None:
        """
        Translates a single saved sentence entry and updates the UI with the translation.

        Args:
            entry_widget (SavedSentenceEntry): The widget containing the saved sentence entry to be translated.
        """
        sentence = entry_widget.get_target_language_text()
        if sentence == "":
            return

        # TODO: Allow multiple languages in parallel in text mode, then retrieve language of specific entry
        translation = self.translator.translate_text(
            texts=[sentence],
            source_lang=self.target_languages[0],
            target_lang=self.source_language,
        )[0]

        entry_widget.set_source_language_text(translation)

    def make_flashcard_from_entry(self, entry_widget: SavedSentenceEntry) -> None:
        """
        Starts a flashcard in the Flashcard Workspace from a saved sentence entry and removes the entry from the list.

        Args:
            entry_widget: The widget containing the saved sentence entry to be converted into a flashcard.
        """
        target_language = entry_widget.get_target_language_text()
        source_language = entry_widget.get_source_language_text()

        self.ui.flashcard_workspace.reset_flashcard_fields()

        # TODO: Make Flashcard Workspace interface cleaner, e.g. new_text_card(question_text, answer_text, question_language, answer_language)
        self.ui.flashcard_workspace.fields["Question Text"].setText(target_language)
        self.ui.flashcard_workspace.fields["Answer Text"].setText(source_language)
        self.ui.flashcard_workspace.fields["Question Language"].setCurrentText(
            self.target_languages[0]
        )
        self.ui.flashcard_workspace.fields["Answer Language"].setCurrentText(
            self.source_language
        )

        entry_widget.remove_button.click()

    def translate_all_entries(self) -> None:
        """
        Translate all saved sentences from the target language to the source language.
        """
        (
            entry_indices,
            sentences,
        ) = self.ui.study_materials.saved_sentences.get_all_saved_sentences()

        if entry_indices == [] or sentences == []:
            return

        translations = self.translator.translate_text(
            texts=sentences,
            source_lang=self.target_languages[0],
            target_lang=self.source_language,
        )

        self.ui.study_materials.saved_sentences.set_all_translations(
            entry_indices, translations
        )

    def add_entry_from_clipboard(self) -> None:
        """
        Add a new sentence entry to the saved sentences from the clipboard.
        """
        sentence = pyperclip.paste()
        sentence = sentence.replace("\n", " ")
        sentence = " ".join(sentence.split())  # Quick way of replacing multiple spaces
        sentence = sentence.replace("­", "")  # Removing soft hyphens
        self.ui.study_materials.saved_sentences.add_entry(sentence)

    def set_up_sentence_bin(self) -> None:
        """
        Set up the sentence bin for saving new sentences.
        """
        self.current_sentence_bin = None
        self.ui.study_materials.saved_sentences.add_new_cards_button.clicked.connect(
            self.open_sentence_bin
        )

    def open_sentence_bin(self) -> None:
        """
        Open a new sentence bin for collecting sentences.

        If a sentence bin is already open, close it before opening a new one.
        """
        # If a SentenceBin is already open, close it first
        if self.current_sentence_bin is not None:
            self.close_sentence_bin()

        # Create a new SentenceBin
        self.current_sentence_bin = SentenceBin()

        self.current_sentence_bin.sentence_added_signal.connect(
            lambda sentence: self.ui.study_materials.saved_sentences.add_entry(sentence)
        )

        self.current_sentence_bin.show()

    def close_sentence_bin(self) -> None:
        """
        Close the currently open sentence bin.
        """
        # Close the current SentenceBin and set current_sentence_bin to None
        if self.current_sentence_bin is not None:
            self.current_sentence_bin.close()
            self.current_sentence_bin.deleteLater()
            self.current_sentence_bin = None

    def set_up_shortcuts(self):

        # TODO: Perhaps track current widget in focus.
        # Note: By default, shortcut context is if parent widget is focused

        # TODO: Put shortcuts in each UI component's code? (rather keep shortcuts together here).

        # TODO: Add shortcuts help info inside the application somewhere.

        # Saved Sentences widget
        if self.mode == "Text":
            self.add_new_sentences_shortcut = QShortcut(QKeySequence("Alt+B"), self.ui)
            self.add_new_sentences_shortcut.activated.connect(
                self.ui.study_materials.saved_sentences.add_new_cards_button.click
            )

            self.add_sentence_from_clipboard_shortcut = QShortcut(
                QKeySequence("Alt+C"), self.ui
            )
            self.add_sentence_from_clipboard_shortcut.activated.connect(
                self.add_entry_from_clipboard
            )

            # TODO: Going down/up in saved sentence entries shortcuts, with say ctrl+up arrow and down arrow.

        # Translation Workspace widget
        self.tw_translate_shortcut = QShortcut(
            QKeySequence("Alt+T"), self.ui.translation_workspace
        )
        self.tw_translate_shortcut.activated.connect(
            self.ui.translation_workspace.translate_button.click
        )

        self.tw_flashcard_shortcut = QShortcut(
            QKeySequence("Alt+F"), self.ui.translation_workspace
        )
        self.tw_flashcard_shortcut.activated.connect(
            self.ui.translation_workspace.flashcard_button.click
        )

        # Flashcard Workspace widget
        self.ui.flashcard_workspace.setFocusPolicy(Qt.StrongFocus)

        self.swap_deck_shortcut = QShortcut(
            QKeySequence("Ctrl+D"), self.ui.flashcard_workspace
        )
        self.swap_deck_shortcut.activated.connect(self.ui.flashcard_workspace.swap_deck)

        self.add_flashcard_shortcut = QShortcut(
            QKeySequence("Ctrl+Return"),
            self.ui.flashcard_workspace,
        )
        self.add_flashcard_shortcut.activated.connect(
            self.ui.flashcard_workspace.add_button.click
        )

        # Dictionary Lookup widget
        self.copy_to_dictionary_lookup_shortcut = QShortcut(
            QKeySequence("Ctrl+L"), self.ui
        )
        self.copy_to_dictionary_lookup_shortcut.activated.connect(
            self.copy_to_dictionary_lookup
        )

        # TODO: Sentence Bin shortcuts

        # TODO: Shortcuts to move focus to different widgets

    def copy_to_dictionary_lookup(self) -> None:
        """
        Copies the current clipboard text to the dictionary lookup line edit and sets the
        focus on the dictionary line edit so the user can easily click `Enter` to search.
        """
        clipboard_text = pyperclip.paste()
        self.ui.dictionary_lookup.dictionary_lookup_lineedit.setText(clipboard_text)
        self.ui.dictionary_lookup.dictionary_lookup_lineedit.setFocus()

    def set_up_all_enter_key_signals(self) -> None:
        """
        Sets up connections for Enter key signals across various UI elements.
        """
        self.ui.dictionary_lookup.dictionary_lookup_lineedit.returnPressed.connect(
            self.ui.dictionary_lookup.search_button.click
        )

        # TODO: Lots more to add! :)

    def delete_empty_decks(self) -> None:
        """
        Deletes any flashcard decks that have no flashcards created.

        Iterates through all decks and checks if the corresponding flashcard creator
        has created any flashcards. If a deck is empty (i.e., contains no flashcards),
        it is deleted.
        """
        for deck in self.decks:
            flashcard_creator = self.flashcard_creators[deck]
            num_flashcards_created = flashcard_creator.number_of_flashcards_created()
            if num_flashcards_created == 0:
                flashcard_creator.delete_deck()
            else:
                print(f"Created {num_flashcards_created} for '{deck}' deck.")

    def clean_temporary_files(self) -> None:
        """
        Cleans up temporary files in the temporary audio folder.
        """
        # Convert the folder path to a Path object
        temp_folder = Path(self.temporary_audio_folder)

        # Loop through every file in the folder
        for file_path in temp_folder.iterdir():
            # Check if the file is a file (not a folder)
            if file_path.is_file():
                # Delete the file
                file_path.unlink()
