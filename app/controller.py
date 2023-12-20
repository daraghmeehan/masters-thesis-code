## Standard library imports
import os
from typing import Dict


## Third-party imports
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QShortcut
from PyQt5.QtGui import QKeySequence

import webbrowser  # For opening links (dictionary searches) in web browser
from bs4 import BeautifulSoup  # For parsing HTML
import pyperclip  # For clipboard operations


## Local imports
from model.model import SubtitleModel

# Translator/Dictionaries
from deep_l.translator import load_translator
from Lexilogos.dictionaries import load_all_tl_to_english_dictionaries

# UI imports
from ui.startup_dialog import StartupDialog
from ui.view import MainWindow
from ui.sentence_bin import SentenceBin

# Flashcard creation functionality
from Flashcards.flashcard_creator import FlashcardCreator
from avi_utils.screenshot_extractor import ScreenshotExtractor
from audio.audio_extractor import AudioExtractor

# Two below to make scaling bigger on small high-res screens
if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class Controller:
    def __init__(self):
        pass

    def run(self):
        """
        Runs the main application process.

        This method orchestrates the setup of language reference tools, initializes
        the user interface, and handles the application's main loop. It also manages
        the setup of media extractors for audiovisual input when working with
        audio-visual Input and performs cleanup operations after execution.

        The process includes:
        - Loading the translator and dictionaries (the language reference tools).
        - Setting up the flashcard creators.
        - Running the startup dialog and parsing the selected options.
        - Initializing the model and UI based on the chosen mode.
        - Executing the application's event loop.
        - Exporting flashcards created and cleaning temporary files.
        """
        # Initialise language reference tools
        self.translator = load_translator()
        self.languages_and_their_dictionaries = load_all_tl_to_english_dictionaries()

        self.temporary_audio_folder = "../temp/audio"
        self.flashcard_media_folder = "../media/flashcards/new"

        # Run and parse the startup dialog, where the user chooses the languages/media they wish to study
        startup_options = self.run_startup_dialog()
        self.parse_startup_options(startup_options)

        # Get ready to make flashcards
        self.flashcard_creators = self.set_up_flashcard_creators(mode=self.mode)

        if self.mode == "AVI":
            # Set up the media extractors
            self.set_up_screenshot_extractor()
            self.set_up_audio_extractor()

        # Set up the model and the view
        self.set_up_model()
        self.set_up_ui()

        # Show the UI and run the event loop
        self.ui.show()
        try:
            self.app.exec_()
        finally:
            # Clean up our work
            self.export_flashcards()
            self.clean_temporary_files()
            pass

    def run_startup_dialog(self):
        startup_app = QApplication([])
        startup_dialog = StartupDialog(self.languages_and_their_dictionaries)
        if startup_dialog.exec_() == QDialog.Accepted:
            startup_options = startup_dialog.get_options()
            return startup_options
        exit()  # If dialog is rejected

    def parse_startup_options(self, startup_options):
        self.mode = startup_options["Mode"]
        self.source_language = startup_options["Source Language"]
        self.target_languages = startup_options["Target Languages"]
        self.languages = [self.source_language] + self.target_languages
        self.dictionaries = startup_options["Dictionaries"]
        if self.mode == "AVI":
            self.video_file = startup_options["Video File"]
            self.audio_tracks = startup_options["Audio Tracks"]
            self.subtitle_files = startup_options["Subtitle Files"]

    def set_up_flashcard_creators(self) -> Dict[str, FlashcardCreator]:
        """
        Sets up flashcard creators for different difficulty levels.

        This method initializes flashcard creators for 'Easy', 'Normal', and 'Hard'
        difficulty levels. Each creator is configured with a specific deck name and
        a set of fields defined elsewhere in the Controller.

        Returns:
            Dict[str, FlashcardCreator]: A dictionary mapping difficulty levels to
            their respective FlashcardCreator instances.
        """
        easy_flashcard_creator = FlashcardCreator(
            deck_name="Languages Easy", fields=self.flashcard_fields
        )
        normal_flashcard_creator = FlashcardCreator(
            deck_name="Languages Normal", fields=self.flashcard_fields
        )
        hard_flashcard_creator = FlashcardCreator(
            deck_name="Languages Hard", fields=self.flashcard_fields
        )

        flashcard_creators = {
            "Easy": easy_flashcard_creator,
            "Normal": normal_flashcard_creator,
            "Hard": hard_flashcard_creator,
        }

        return flashcard_creators

    def set_up_screenshot_extractor(self):
        self.screenshot_extractor = ScreenshotExtractor(self.video_file)

    def set_up_audio_extractor(self):
        self.audio_extractor = AudioExtractor(self.temporary_audio_folder)
        self.audio_extractor.extract_all_language_tracks(
            self.video_file, self.audio_tracks
        )  # Extract the audio tracks of the video file

    def set_up_model(self):
        if self.mode == "AVI":
            self.model = SubtitleModel(self.subtitle_files, self.source_language)
        elif self.mode == "Text":
            pass

    def set_up_ui(self):
        self.app = QApplication([])

        if self.mode == "AVI":
            main_window_title = self.video_file
        else:
            main_window_title = self.target_languages[0]

        # Set up the view
        self.ui = MainWindow(window_title=main_window_title, mode=self.mode)

        # Set up key widgets of the UI
        self.set_up_study_materials()
        self.set_up_translation_workspace()
        self.set_up_dictionary_lookup()
        self.set_up_flashcard_workspace()

        # Set up UI workflow
        self.set_up_shortcuts()
        self.set_up_all_enter_key_signals()

    def set_up_study_materials(self):
        if self.mode == "AVI":
            self.set_up_subtitle_workspace()
        self.set_up_saved_sentences()

    def set_up_subtitle_workspace(self):
        pass

    def set_up_saved_sentences(self):
        self.set_up_sentence_bin()

        self.ui.study_materials.saved_sentences.translate_entry_signal.connect(
            self.translate_entry
        )
        self.ui.study_materials.saved_sentences.make_flashcard_from_entry_signal.connect(
            self.make_flashcard_from_entry
        )

        self.ui.study_materials.saved_sentences.translate_all_button.clicked.connect(
            self.translate_all_entries
        )

        self.ui.study_materials.saved_sentences.add_new_from_clipboard_button.clicked.connect(
            self.add_entry_from_clipboard
        )

    def translate_entry(self, entry_widget):
        """Entry from saved_sentences_1"""
        sentence = entry_widget.get_target_language_text()
        print(f"Got sentence: {sentence}")
        ##!! set language dynamically
        translation = self.translator.translate_text(
            text=sentence,
            source_lang=self.source_language,
            target_lang=self.target_languages[0],  ##!! change?
        ).text
        entry_widget.set_source_language_text(translation)

    def make_flashcard_from_entry(self, entry_widget):
        target_language = entry_widget.get_target_language_text()
        source_language = entry_widget.get_source_language_text()

        self.ui.flashcard_workspace.reset_flashcard_fields()

        self.ui.flashcard_workspace.target_textedit.setText(target_language)
        self.ui.flashcard_workspace.source_textedit.setText(source_language)

        entry_widget.remove_button.click()

    def translate_all_entries(self):
        (
            entry_indices,
            sentences,
        ) = self.ui.study_materials.saved_sentences.get_all_saved_sentences()

        if entry_indices == [] or sentences == []:
            return

        ##!! set language dynamically
        translations = self.translator.translate_text(
            text=sentences,
            source_lang=self.source_language,
            target_lang=self.target_languages[0],  ##!! how to know which?
        )
        translations = [translation.text for translation in translations]

        self.ui.study_materials.saved_sentences.set_all_translations(
            entry_indices, translations
        )

    def set_up_translation_workspace(self):
        self.ui.translation_workspace.set_languages(
            languages=self.languages,
            target_language=self.target_languages[0],
            source_language=self.source_language,
        )

        self.ui.translation_workspace.translate_button.clicked.connect(
            self.translate_from_workspace
        )

        self.ui.translation_workspace.flashcard_button.clicked.connect(
            self.make_flashcard_from_workspace
        )

    def translate_from_workspace(self):
        target_language_text = self.ui.translation_workspace.get_target_language_text()
        if target_language_text == "":
            return

        target_language = self.ui.translation_workspace.get_target_language()
        source_language = self.ui.translation_workspace.get_source_language()

        if target_language == source_language:
            return  # don't do anything if translating between same language

        try:
            translation = self.translator.translate_text(
                text=target_language_text,
                source_lang=source_language,
                target_lang=target_language,
            ).text
        except:
            translation = ""

        self.ui.translation_workspace.set_source_language_text(translation)

    def make_flashcard_from_workspace(self):
        target_language = self.ui.translation_workspace.get_target_language_text()
        source_language = self.ui.translation_workspace.get_source_language_text()

        self.ui.flashcard_workspace.reset_flashcard_fields()

        self.ui.flashcard_workspace.target_textedit.setText(target_language)
        self.ui.flashcard_workspace.source_textedit.setText(source_language)

        self.ui.translation_workspace.clear_workspace()

    def set_up_flashcard_workspace(self):
        self.ui.flashcard_workspace.deck_dropdown.addItems(["Easy", "Normal", "Hard"])
        ##!!add fields dynamically along with data type
        self.ui.flashcard_workspace.add_button.clicked.connect(self.add_flashcard)
        # self.ui.flashcard_workspace.edit_button.clicked.connect(self.edit_previous_flashcards)

    def add_flashcard(self):
        # Saving the image/audio of the card
        self.save_card_media()

        # Extracting the card information from the UI
        card_as_dict = self.extract_card_from_workspace()
        if card_as_dict == {}:
            return

        # Retrieving the chosen deck
        deck = self.ui.flashcard_workspace.deck_dropdown.currentText()

        # Adding our card to the appropriate deck
        self.flashcard_creators[deck].add_flashcard(card_as_dict)

        self.ui.flashcard_workspace.reset_flashcard_fields()

    def save_card_media(self):
        pass

    def extract_card_from_workspace(self):
        # reject if target and source languages are missing
        target_language_field_html = (
            self.ui.flashcard_workspace.target_textedit.toHtml()
        )
        target_language_field_html = target_language_field_html.replace("\n", "<br>")
        target_language_field = extract_bold_formatting(target_language_field_html)

        source_language_field = (
            self.ui.flashcard_workspace.source_textedit.toPlainText()
        )
        source_language_field = source_language_field.replace("\n", "<br>")

        if target_language_field == "" or source_language_field == "":
            print("Need both target language and source language! Rejecting card.")
            return

        # creating card from fields in UI
        card_as_dict = {
            "Target Language": target_language_field,
            "Source Language": source_language_field,
            "Answer Hint": self.ui.flashcard_workspace.answer_hint_lineedit.text(),
            "Example Sentence(s)": self.ui.flashcard_workspace.example_sentence_textedit.toPlainText().replace(
                "\n", "<br>"
            ),
            "Other Forms": self.ui.flashcard_workspace.other_forms_textedit.toPlainText().replace(
                "\n", "<br>"
            ),
            "Extra Info": self.ui.flashcard_workspace.extra_info_textedit.toPlainText().replace(
                "\n", "<br>"
            ),
            "Pronunciation": self.ui.flashcard_workspace.pronunciation_lineedit.text(),
            "TL Name": self.target_languages[0],
            "SL Name": self.source_language,
        }

    def export_flashcards(self):
        for flashcard_creator in self.self.flashcard_creators.values():
            flashcard_creator.export_deck()

    def set_up_dictionary_lookup(self):
        self.ui.dictionary_lookup.set_up_dictionaries(self.dictionaries)
        self.ui.dictionary_lookup.search_button.clicked.connect(self.look_up_word)

    def look_up_word(self):
        word = self.ui.dictionary_lookup.dictionary_lookup_lineedit.text()
        word = word.replace("­", "")  # removing soft hyphens!

        if word == "":
            return

        dictionaries_to_search = []

        ##!! put this in dictionary_lookup!
        checkbox_layout = self.ui.dictionary_lookup.dictionary_checkbox_layout
        for i in range(checkbox_layout.count()):
            checkbox = checkbox_layout.itemAt(i).widget()
            if checkbox.isChecked():
                dictionaries_to_search.append(checkbox.text())

        for dictionary in dictionaries_to_search:
            formatting = self.languages_and_their_dictionaries[self.target_language][
                dictionary
            ]
            search_address = formatting[0] + word + formatting[1]
            webbrowser.open(
                search_address,  # autoraise=False
            )
            ##?? any way of setting focus on this window??

    def set_up_sentence_bin(self):
        self.current_sentence_bin = None
        self.ui.study_materials.saved_sentences.add_new_cards_button.clicked.connect(
            self.open_sentence_bin
        )

    # @pydtSlot()
    def open_sentence_bin(self):
        # If a SentenceBin is already open, close it first
        if self.current_sentence_bin is not None:
            self.close_sentence_bin()

        # Create a new SentenceBin
        self.current_sentence_bin = SentenceBin()

        self.current_sentence_bin.sentence_added_signal.connect(
            lambda sentence: self.ui.study_materials.saved_sentences.add_entry(sentence)
        )

        self.current_sentence_bin.show()

    def close_sentence_bin(self):
        # Close the current SentenceBin and set current_sentence_bin to None
        if self.current_sentence_bin is not None:
            self.current_sentence_bin.close()
            self.current_sentence_bin.deleteLater()
            self.current_sentence_bin = None

    def set_up_shortcuts(self):
        ##dd By default, shortcut context is if parent widget is focused

        # saved sentences widget
        ##!! current widget in focus function (need to track it)
        ## instead putting shortcut in each one (rather keep shortcuts together)
        ##!! also want going down/up entries with say ctrl+up arrow and down arrow

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

        # translation workspace widget
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

        # flashcard_workspace widget
        self.swap_deck_shortcut = QShortcut(
            QKeySequence("Ctrl+D"), self.ui.flashcard_workspace
        )
        self.swap_deck_shortcut.activated.connect(
            self.ui.flashcard_workspace.swap_options
        )

        self.add_flashcard_shortcut = QShortcut(
            QKeySequence("Ctrl+Return"), self.ui.flashcard_workspace
        )
        self.add_flashcard_shortcut.activated.connect(
            self.ui.flashcard_workspace.add_button.click
        )

        # dictionary_lookup widget
        self.copy_to_dictionary_lookup_shortcut = QShortcut(
            QKeySequence("Ctrl+L"), self.ui
        )
        self.copy_to_dictionary_lookup_shortcut.activated.connect(
            self.copy_to_dictionary_lookup
        )

        ##?? sentence bin widget

        ##!! shortcuts to move focus

    def add_entry_from_clipboard(self):
        sentence = pyperclip.paste()
        sentence = sentence.replace("\n", " ")
        sentence = " ".join(sentence.split())  # quick way of replacing multiple spaces
        sentence = sentence.replace("­", "")  # removing soft hyphens!
        self.ui.study_materials.saved_sentences.add_entry(sentence)

    ##?? how to teach user
    def copy_to_dictionary_lookup(self):
        self.ui.dictionary_lookup.dictionary_lookup_lineedit.setText(pyperclip.paste())
        self.ui.dictionary_lookup.dictionary_lookup_lineedit.setFocus()

    def set_up_all_enter_key_signals(self):
        self.ui.dictionary_lookup.dictionary_lookup_lineedit.returnPressed.connect(
            self.ui.dictionary_lookup.search_button.click
        )

    def clean_temporary_files(self):
        # Loop through every file in the folder
        for file_name in os.listdir(self.temporary_audio_folder):
            # Construct the full path of the file
            file_path = os.path.join(self.temporary_audio_folder, file_name)
            # Check if the file is a file (not a folder)
            if os.path.isfile(file_path):
                # Delete the file
                os.remove(file_path)


def extract_bold_formatting(html_field):
    if html_field == "":
        return ""

    soup = BeautifulSoup(html_field, "html.parser", from_encoding="utf-8")
    p = soup.find("p")

    # replacing span with strong
    for span_tag in p.find_all("span"):
        strong_tag = soup.new_tag("strong")
        strong_tag.string = span_tag.string
        span_tag.replace_with(strong_tag)

    field = "".join(str(c) for c in p.contents)
    return field
