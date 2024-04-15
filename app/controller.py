## Standard library imports
import os, time
from typing import Dict


## Third-party imports
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QDialog, QShortcut
from PyQt5.QtGui import QKeySequence

import webbrowser  # For opening links (dictionary searches) in web browser
import pyperclip  # For clipboard operations


## Local imports
from model.model import AVIModel

# Translator/Dictionaries
from deep_l.translator import load_translator
from lexilogos.dictionaries import load_all_target_to_english_dictionaries

# UI imports
from ui.startup_dialog import StartupDialog
from ui.view import MainWindow
from ui.flashcard_workspace import ScreenshotViewer, AudioViewer
from ui.sentence_bin import SentenceBin

# Flashcard creation functionality
from flashcards.flashcard_templates import read_flashcard_templates
from flashcards.flashcard_creator import FlashcardCreator

from avi_utils.screenshot_extractor import ScreenshotExtractor
from avi_utils.audio_player import AudioPlayer
from audio.audio_extractor import AudioExtractor

# Two below to make scaling bigger on small high-res screens
if hasattr(Qt, "AA_EnableHighDpiScaling"):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, "AA_UseHighDpiPixmaps"):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


gg_startup_options = {
    "Mode": "AVI",
    "Video File": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.mp4",
    "Source Language": "English",
    "Target Languages": [
        "Spanish",
        # "Dutch",
        # "Czech",
        # "Italian",
        "Japanese",
        "French",
        # "Chinese",
        # "Polish",
        # "Indonesian",
        # "Portuguese",
        # "Swedish",
        # "Turkish",
        # "Chinese (Traditional)",
    ],
    "Audio Tracks": {
        "English": "None",
        # "Dutch": "None",
        # "Czech": "None",
        "Spanish": "None",
        # "Italian": "None",
        "Japanese": "None",
        # "Spanish": "spa",
        # "Italian": "ita",
        # "Japanese": "jpn",
        # "Chinese": "None",
        "French": "None",
        # "Polish": "None",
        # "Indonesian": "None",
        # "Portuguese": "None",
        # "Swedish": "None",
        # "Turkish": "None",
        # "Chinese (Traditional)": "None",
    },
    "Subtitle Files": {
        "Reference": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.en.srt",
        "English": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.en.srt",
        "Spanish": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.es.srt",
        # "Dutch": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.nl.srt",
        # "Czech": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.cs.srt",
        # "Italian": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.it.srt",
        "Japanese": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.ja.srt",
        "French": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.fr.srt",
        # "Chinese": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.zh-Hans.srt",
        # "Polish": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.pl.srt",
        # "Indonesian": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.id.srt",
        # "Portuguese": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.pt.srt",
        # "Swedish": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.sv.srt",
        # "Turkish": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.tr.srt",
        # "Chinese (Traditional)": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.zh-Hant.srt",
    },
    "Dictionaries": {
        "Spanish": ["SpanishDict", "Collins"],
        # "Dutch": ["Van Dale", "MijnWoordenboek"],
        # "Czech": ["Fake"],
        # "Italian": ["Collins"],
        "Japanese": ["Fake"],
        # "Chinese": ["Fake"],
        "French": ["Larousse", "WordReference"],
        # "Polish": [],
        # "Indonesian": [],
        # "Portuguese": [],
        # "Swedish": [],
        # "Turkish": [],
        # "Chinese (Traditional)": [],
    },
}

peppa_startup_options = {
    "Mode": "AVI",
    "Video File": "C:/Stuff/Peppa Pig/Daddy loses his glasses.mp4",
    "Source Language": "English",
    "Target Languages": ["Dutch", "Italian"],
    "Audio Tracks": {
        "English": "eng",
        "Dutch": "dut",
        "Italian": "ita",
        # "English": "None",
        # "Dutch": "None",
        # "Italian": "None",
    },
    "Subtitle Files": {
        "Reference": "C:/Stuff/Peppa Pig/[English] Daddy loses his glasses.srt",
        "English": "C:/Stuff/Peppa Pig/[English] Daddy loses his glasses.srt",
        "Dutch": "C:/Stuff/Peppa Pig/[Dutch] Daddy loses his glasses.srt",
        "Italian": "C:/Stuff/Peppa Pig/[Italian] Daddy loses his glasses.srt",
    },
    "Dictionaries": {
        "Dutch": ["Van Dale", "MijnWoordenboek"],
        "Italian": ["Reverso", "Collins", "WordReference"],
    },
}

text_mode_options = {
    "Mode": "Text",
    "Source Language": "English",
    "Target Languages": ["Spanish"],
    "Dictionaries": {
        "Spanish": ["WordReference", "Collins"],
    },
}


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
        self.target_to_english_dictionaries = load_all_target_to_english_dictionaries()

        # # Run and parse the startup dialog, where the user chooses the languages/media they wish to study
        # startup_options = self.run_startup_dialog()

        # For quicker testing
        # startup_options = gg_startup_options
        # startup_options = peppa_startup_options
        startup_options = text_mode_options

        self.parse_startup_options(startup_options)
        if self.mode == "Export Media":
            # self.export_media (all_exports : List)??
            return

        self.translator = load_translator()
        # !!
        self.flashcard_output_folder = "../media/flashcards/new_cards"

        # Get ready to make flashcards
        flashcard_templates_path = "resources/flashcards/flashcard_templates.json"
        flashcard_template = self.load_flashcard_template(flashcard_templates_path)
        self.parse_flashcard_template(flashcard_template)
        self.flashcard_creators = self.set_up_flashcard_creators()

        if self.mode == "AVI":
            self.temporary_audio_folder = "../temp/audio"
            self.flashcard_audio_folder = "../media/flashcards/flashcard_audio"
            self.flashcard_image_folder = "../media/flashcards/flashcard_images"
            self.avi_practice_audio_folder = "../media/audio"

            # Set up the media extractors
            self.set_up_screenshot_extractor()
            self.set_up_audio_extractor()

            # To play and export subtitle audio
            self.audio_player = AudioPlayer()

        # Set up the model and the view
        self.set_up_model()
        self.set_up_ui()

        # Show the UI and run the event loop
        self.ui.show()
        try:
            self.app.exec_()
        finally:
            # Clean up our work
            self.delete_empty_decks()
            if self.mode == "AVI":
                self.clean_temporary_files()
            pass

    def run_startup_dialog(self):
        startup_app = QApplication([])
        startup_dialog = StartupDialog(self.target_to_english_dictionaries)
        if startup_dialog.exec_() == QDialog.Accepted:
            startup_options = startup_dialog.get_options()
            return startup_options
        exit()  # If dialog is rejected

    def parse_startup_options(self, startup_options):
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

    def load_flashcard_template(self, flashcard_templates_path):
        """
        Loads the JSON flashcard templates and extracts the selected mode's template.

        :return: The loaded template as a Python dictionary.
        """

        flashcard_templates = read_flashcard_templates(flashcard_templates_path)

        flashcard_template = flashcard_templates["languages_template"]

        return flashcard_template

    def parse_flashcard_template(self, flashcard_template):
        self.flashcard_fields = flashcard_template["fields"]
        self.required_fields = flashcard_template["required_fields"]
        self.decks = flashcard_template["decks"]

    def set_up_flashcard_creators(self):
        flashcard_creators = {}

        flashcard_field_names = list(self.flashcard_fields.keys())
        if "Tags" in flashcard_field_names:
            flashcard_field_names.remove("Tags")
        for deck in self.decks:
            flashcard_creator = FlashcardCreator(
                deck_name=f"({self.mode}) Languages {deck}",
                fields=flashcard_field_names,
            )
            flashcard_creators[deck] = flashcard_creator

        return flashcard_creators

    def set_up_screenshot_extractor(self):
        self.screenshot_extractor = ScreenshotExtractor(self.video_file)

    def set_up_audio_extractor(self):
        self.audio_extractor = AudioExtractor(self.temporary_audio_folder)
        self.audio_extractor.extract_all_language_tracks(
            self.video_file, self.audio_tracks
        )  # Extract the audio tracks of the video file

    def set_up_model(self):
        if self.mode == "Text":
            pass
        elif self.mode == "AVI":
            self.model = AVIModel(self.subtitle_files)

    def set_up_ui(self):
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

    def set_up_flashcard_workspace(self):
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

    def translate_question_text(self):
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
            question_text, question_language, answer_language
        ).text

        self.ui.flashcard_workspace.fields["Answer Text"].setText(answer_text)

    def play_flashcard_audio(self, audio_path):
        self.audio_player.stop()

        if audio_path != self.audio_player.get_audio_path():
            self.audio_player.reset_player()
            self.audio_player.update_audio(audio_path)

        self.audio_player.play()

    def stop_flashcard_audio(self):
        self.audio_player.stop()

    def change_flashcard_audio_time(self, start_or_end_time, adjustment):
        # Reextract flashcard audio file with different start/end time
        pass

    def add_flashcard(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")  # For uniquely naming files

        flashcard = {}
        for field_name, field_info in self.flashcard_fields.items():
            if field_info["type"] == "Media":
                if self.mode == "AVI":
                    media_path = self.save_card_media(field_name, timestamp)
                    field_data = media_path
                    if field_name == "Audio":
                        field_data = "[sound:" + field_data + "]"
                else:
                    field_data = ""
            elif field_name == "Tags":
                # Tags need to be set separately
                continue
            else:
                field_data = self.ui.flashcard_workspace.extract_field_data(field_name)
            flashcard[field_name] = field_data

        # Ensuring all our required fields have some data
        for required_field in self.required_fields:
            if flashcard[required_field] == "":
                ##!! If required fields blank, still might have saved card media!
                print(
                    f"{required_field} is a required field but is blank! Rejecting card..."
                )
                return

        # Retrieving the chosen deck
        deck = self.ui.flashcard_workspace.deck_dropdown.currentText()

        # print(flashcard)

        # Adding our card to the appropriate deck
        self.flashcard_creators[deck].add_flashcard(flashcard)

        self.ui.flashcard_workspace.reset_flashcard_fields()

    def save_card_media(self, field_name, timestamp):
        filename = ""  # Media flashcard fields must point to the filename
        media_widget = self.ui.flashcard_workspace.fields[field_name]

        if (
            isinstance(media_widget, ScreenshotViewer)
            and media_widget.has_screenshots()
        ):
            file_extension = ".jpg"
            # "_languages_" is code to be able to find language card pictures easily in Anki media folder
            filename = "_languages_" + timestamp + file_extension
            path = os.path.join(self.flashcard_image_folder, filename)
            media_widget.save_screenshot(path)

        elif isinstance(media_widget, AudioViewer) and media_widget.has_audio():
            audio_path = self.ui.flashcard_workspace.fields["Audio"].get_audio_path()

            if self.audio_player.get_audio_path != audio_path:
                self.audio_player.update_audio(audio_path)

            file_extension = ".mp3"
            # "_languages_" is code to be able to find language card pictures easily in Anki media folder
            filename = "_languages_" + timestamp + file_extension
            path = os.path.join(self.flashcard_audio_folder, filename)
            self.audio_player.save_audio(path)

        return filename

    def edit_previous_flashcards(self):
        pass

    def set_up_translation_workspace(self):
        self.ui.translation_workspace.set_languages(
            languages=self.languages,
            source_language=self.target_languages[0],
            target_language=self.source_language,
        )

        self.ui.translation_workspace.translate_button.clicked.connect(
            self.translate_from_workspace
        )

        self.ui.translation_workspace.flashcard_button.clicked.connect(
            self.make_flashcard_from_workspace
        )

    def translate_from_workspace(self):
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
                text=source_language_text,
                source_lang=source_language,
                target_lang=target_language,
            ).text
        except:
            translation = ""

        self.ui.translation_workspace.set_target_language_text(translation)

    def make_flashcard_from_workspace(self):
        ## should rename these??
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
            target_language
        )
        self.ui.flashcard_workspace.fields["Answer Language"].setCurrentText(
            source_language
        )

        self.ui.translation_workspace.clear_workspace()

    def set_up_dictionary_lookup(self):
        self.ui.dictionary_lookup.set_up_dictionaries(self.dictionaries)
        self.ui.dictionary_lookup.search_button.clicked.connect(self.look_up_word)
        self.ui.dictionary_lookup.search_requested.connect(
            self.look_up_word_in_one_dictionary
        )

    def look_up_word(self):
        word = self.ui.dictionary_lookup.get_text()

        if word == "":
            return

        # dictionaries_to_search = []

        # ##!! put this in dictionary_lookup!
        # checkbox_layout = self.ui.dictionary_lookup.dictionary_checkbox_layout
        # for i in range(checkbox_layout.count()):
        #     checkbox = checkbox_layout.itemAt(i).widget()
        #     if checkbox.isChecked():
        #         dictionaries_to_search.append(checkbox.text())

        language = self.ui.dictionary_lookup.get_language()
        dictionaries_to_search = self.ui.dictionary_lookup.get_dictionaries()

        for dictionary in dictionaries_to_search:
            formatting = self.target_to_english_dictionaries[language][dictionary][
                "url"
            ]
            search_address = formatting[0] + word + formatting[1]
            webbrowser.open(
                search_address,  # autoraise=False
            )
            ##?? any way of setting focus on this window??

    def look_up_word_in_one_dictionary(self, language, dictionary):
        word = self.ui.dictionary_lookup.get_text()

        if word == "":
            return

        formatting = self.target_to_english_dictionaries[language][dictionary]["url"]
        search_address = formatting[0] + word + formatting[1]
        webbrowser.open(
            search_address,  # autoraise=False
        )

    def set_up_study_materials(self):
        if self.mode == "AVI":
            # import sys
            # sys.argv.append(self.model) ## For testing

            self.set_up_subtitle_workspace()

            initial_alignment = self.model.get_alignment()
            self.set_subtitle_alignment(initial_alignment)
        elif self.mode == "Text":
            self.set_up_saved_sentences()

    def set_up_subtitle_workspace(self):
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

    def make_flashcard_from_subtitle(self, language, index):
        ##!! rename index/indices to number/numbers
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
            self.audio_player.reset_player()  # Otherwise we can't extract the segment if the last one played was also a flashcard one
            audio_segment_path = self.audio_extractor.extract_segment(
                language, start_time, end_time, is_for_flashcard=True
            )
            self.ui.flashcard_workspace.fields["Audio"].update_audio(audio_segment_path)
            self.audio_player.update_audio(audio_segment_path)

    def play_subtitle_audio(self, language, index):
        if self.audio_tracks[language] == "None":
            return

        self.audio_player.stop()
        self.audio_player.reset_player()

        subtitle = self.model.get_subtitle(language, index)

        audio_segment_path = self.audio_extractor.extract_segment(
            language, subtitle.start_time, subtitle.end_time, is_for_flashcard=False
        )

        self.audio_player.update_audio(audio_segment_path)
        self.audio_player.play()

    def set_subtitle_alignment(self, alignment):
        self.ui.study_materials.subtitle_workspace.clear_workspace()

        for entry in alignment:
            subtitles = {
                language: {"indices": [], "texts": []} for language in self.languages
            }
            for language in self.languages:
                all_subtitle_indices = entry["subtitle_indices"][language]
                if all_subtitle_indices == []:
                    continue

                all_subtitle_texts = []
                for subtitle_index in all_subtitle_indices:
                    subtitle_text = self.model.get_subtitle(
                        language, subtitle_index
                    ).text
                    all_subtitle_texts.append(subtitle_text)

                subtitles[language]["indices"] = all_subtitle_indices
                subtitles[language]["texts"] = all_subtitle_texts

            self.ui.study_materials.subtitle_workspace.add_entry(subtitles)

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
        if sentence == "":
            return
        ##!! set language dynamically
        translation = self.translator.translate_text(
            text=sentence,
            source_lang=self.target_languages[0],
            target_lang=self.source_language,  ##!! change?
        ).text
        entry_widget.set_source_language_text(translation)

    def make_flashcard_from_entry(self, entry_widget):
        target_language = entry_widget.get_target_language_text()
        source_language = entry_widget.get_source_language_text()

        self.ui.flashcard_workspace.reset_flashcard_fields()

        self.ui.flashcard_workspace.fields["Question Text"].setText(target_language)
        self.ui.flashcard_workspace.fields["Answer Text"].setText(source_language)

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
            source_lang=self.target_languages[0],
            target_lang=self.source_language,
        )
        translations = [translation.text for translation in translations]

        self.ui.study_materials.saved_sentences.set_all_translations(
            entry_indices, translations
        )

    def add_entry_from_clipboard(self):
        sentence = pyperclip.paste()
        sentence = sentence.replace("\n", " ")
        sentence = " ".join(sentence.split())  # quick way of replacing multiple spaces
        sentence = sentence.replace("­", "")  # removing soft hyphens!
        self.ui.study_materials.saved_sentences.add_entry(sentence)

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
        self.swap_deck_shortcut.activated.connect(self.ui.flashcard_workspace.swap_deck)

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

    ##?? how to teach user
    def copy_to_dictionary_lookup(self):
        self.ui.dictionary_lookup.dictionary_lookup_lineedit.setText(pyperclip.paste())
        self.ui.dictionary_lookup.dictionary_lookup_lineedit.setFocus()

    def set_up_all_enter_key_signals(self):
        self.ui.dictionary_lookup.dictionary_lookup_lineedit.returnPressed.connect(
            self.ui.dictionary_lookup.search_button.click
        )

    def export_episode(self):
        language_order = ["English", "Spanish", "French"]
        speaking_times = self.model.get_all_speaking_times()
        for language in language_order:
            audio_track = self.audio_tracks[language]
            if audio_track == "None":
                continue
            self.audio_something.extract_audio(speaking_times)

    def delete_empty_decks(self):
        for deck in self.decks:
            flashcard_creator = self.flashcard_creators[deck]
            if flashcard_creator.number_of_flashcards_created() == 0:
                flashcard_creator.delete_deck()

    def clean_temporary_files(self):
        # Loop through every file in the folder
        for file_name in os.listdir(self.temporary_audio_folder):
            # Construct the full path of the file
            file_path = os.path.join(self.temporary_audio_folder, file_name)
            # Check if the file is a file (not a folder)
            if os.path.isfile(file_path):
                # Delete the file
                os.remove(file_path)
