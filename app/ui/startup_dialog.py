from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
import json

from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QStackedWidget,
    QWidget,
    QTabWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QCheckBox,
    QComboBox,
    QPushButton,
    QLineEdit,
    QLabel,
    QFrame,
    QSizePolicy,
)

import ffmpeg

LANGUAGE_LEARNING_MATERIAL_PATH = (
    r"C:\Stuff\UniversaLearn\LanguageRepo\Language Learning Material"
)

MODE_PAGE_INDEX = 0
TEXT_PAGE_INDEX = 1
AVI_PAGE_INDEX = 2
DICTIONARY_PAGE_INDEX = 3


all_target_languages = [
    "Arabic",
    "Bulgarian",
    "Chinese",
    "Czech",
    "Danish",
    "Dutch",
    "Estonian",
    "Finnish",
    "French",
    "German",
    "Greek",
    "Hungarian",
    "Indonesian",
    "Italian",
    "Japanese",
    "Korean",
    "Latvian",
    "Lithuanian",
    "Norwegian",
    "Polish",
    "Portuguese",
    "Romanian",
    "Russian",
    "Slovak",
    "Slovenian",
    "Spanish",
    "Swedish",
    "Turkish",
    "Ukrainian",
]


# TODO: Refactor this by placing elsewhere (as used in more places than here).
def get_audio_tracks(filename):
    """Get a list of audio stream names from a video file"""
    tracks = ffmpeg.probe(filename)["streams"]
    audio_tracks = [s["tags"]["language"] for s in tracks if s["codec_type"] == "audio"]
    return audio_tracks


class StartupDialog(QDialog):
    """
    A dialog that allows the user to choose between different study modes and configure settings for each mode.

    Attributes:
        target_to_english_dictionaries (Dict[str, Dict[str, Any]]): A dictionary containing language-specific dictionary info.
        startup_options (Dict[str, Any]): A dictionary to store startup options.
        stacked_widget (QStackedWidget): A widget to manage the different pages of the dialog.
        choose_mode_page (QWidget): The initial page where the user selects the study mode.
        text_options_page (TextWidget): The page for configuring text-based study options.
        avi_options_page (AVIWidget): The page for configuring audiovisual input options.
        dictionary_options_page (DictionaryChoicesWidget): The page for selecting dictionaries for translation.
    """

    def __init__(self, target_to_english_dictionaries: Dict[str, Dict[str, Any]]):
        """
        Initialise the StartupDialog.

        Args:
            target_to_english_dictionaries (Dict[str, Dict[str, Any]]): A dictionary containing all the dictionary info.
        """
        super().__init__()
        self.target_to_english_dictionaries = target_to_english_dictionaries
        self.startup_options = {"Mode": None}
        self.initUI()

    def initUI(self) -> None:
        """
        Set up the user interface of the dialog, including the different pages for study mode selection and options.
        """
        self.setWindowTitle("Startup Dialog")

        # TODO: Set better sizing possibly.
        # # Set initial size of the dialog
        # self.resize(300, 200)  # Set the initial width and height as desired
        # self.move(390, 50)

        # # Set minimum and maximum sizes for the dialog
        # self.setMinimumSize(300, 200)  # Set the minimum width and height
        # # self.setMaximumSize(800, 600)  # Set the maximum width and height

        # Allow resizing of the dialog
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a stacked widget to hold the different pages of the dialog
        self.stacked_widget = QStackedWidget()
        self.choose_mode_page = QWidget()
        self.text_options_page = TextWidget()
        self.avi_options_page = AVIWidget()
        self.dictionary_options_page = DictionaryChoicesWidget(
            self.target_to_english_dictionaries
        )

        self.stacked_widget.addWidget(self.choose_mode_page)
        self.stacked_widget.addWidget(self.text_options_page)
        self.stacked_widget.addWidget(self.avi_options_page)
        self.stacked_widget.addWidget(self.dictionary_options_page)

        # Choose mode page
        self.mode_label = QLabel("Choose a study mode:")
        self.text_button = QPushButton("Text (Basic Mode)")
        self.avi_button = QPushButton("Audiovisual Input")
        self.export_media_button = QPushButton("Export Media")
        self.mode_layout = QVBoxLayout()
        self.mode_layout.addWidget(self.mode_label)
        self.mode_layout.addWidget(self.text_button)
        self.mode_layout.addWidget(self.avi_button)
        self.mode_layout.addWidget(self.export_media_button)
        self.choose_mode_page.setLayout(self.mode_layout)

        ## Connecting signals and slots

        # Connecting buttons on choose mode page
        self.text_button.clicked.connect(self.text_mode_selected)
        self.avi_button.clicked.connect(self.avi_mode_selected)
        self.export_media_button.clicked.connect(self.export_media_mode_selected)

        # Connecting back buttons
        self.text_options_page.back_button.clicked.connect(self.reset_to_mode_page)
        self.avi_options_page.back_button.clicked.connect(self.reset_to_mode_page)
        self.dictionary_options_page.back_button.clicked.connect(
            self.go_back_from_dictionary_options
        )

        # Connecting confirm buttons
        self.text_options_page.confirm_button.clicked.connect(
            self.text_options_confirmed
        )
        self.avi_options_page.confirm_button.clicked.connect(self.avi_options_confirmed)
        self.dictionary_options_page.confirm_button.clicked.connect(
            self.dictionary_options_confirmed
        )

        # Set the layout of the main dialog
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def reset_to_mode_page(self) -> None:
        self.startup_options = {"Mode": None}  # Remove all saved options
        self.show_mode_page()

    def reset_to_text_page(self) -> None:
        self.startup_options = {"Mode": "Text"}
        self.show_text_page()

    def reset_to_avi_page(self) -> None:
        self.startup_options = {"Mode": "AVI"}
        self.show_avi_page()

    def show_mode_page(self) -> None:
        self.stacked_widget.setCurrentIndex(MODE_PAGE_INDEX)

    def show_text_page(self) -> None:
        self.stacked_widget.setCurrentIndex(TEXT_PAGE_INDEX)

    def show_avi_page(self) -> None:
        self.stacked_widget.setCurrentIndex(AVI_PAGE_INDEX)
        self.adjustSize()

    def show_dictionary_page(self) -> None:
        self.stacked_widget.setCurrentIndex(DICTIONARY_PAGE_INDEX)

    def text_mode_selected(self) -> None:
        self.startup_options["Mode"] = "Text"
        self.show_text_page()

    def avi_mode_selected(self) -> None:
        self.startup_options["Mode"] = "AVI"
        self.show_avi_page()

    def export_media_mode_selected(self) -> None:
        self.startup_options["Mode"] = "Export Media"
        self.accept()  # Accept dialog

    def text_options_confirmed(self) -> None:
        """
        Handles the confirmation of text options by retrieving the selected source and target languages,
        updating the startup options, and navigating to the dictionary options page.
        """
        source_language, target_language = self.text_options_page.get_languages()
        self.startup_options["Source Language"] = source_language
        self.startup_options["Target Languages"] = [target_language]
        self.dictionary_options_page.set_languages([target_language])
        self.show_dictionary_page()

    def avi_options_confirmed(self) -> None:
        """
        Handles the confirmation of AVI options by validating the selected video, audio, and subtitle files,
        updating the startup options, and navigating to the dictionary options page.

        Returns immediately if required options are not provided.
        """
        avi_options = self.avi_options_page.get_all_options()

        # print(avi_options)

        if not avi_options["Video File"]:
            # Don't allow confirming is no video has been chosen
            return

        source_language = avi_options["Source Language"]
        target_language_1 = avi_options["Target Languages"][0]

        if not avi_options["Subtitle Files"][target_language_1]:
            # Don't allow confirming if we are missing target language subtitles
            return

        self.startup_options.update(avi_options)

        target_languages = self.startup_options["Target Languages"]

        self.dictionary_options_page.set_languages(target_languages)
        self.show_dictionary_page()

    def dictionary_options_confirmed(self) -> None:
        """
        Handles the confirmation of dictionary options by updating the startup options
        with the selected dictionaries and accepting the dialog.
        """
        dictionary_options = self.dictionary_options_page.get_dictionaries()

        self.startup_options["Dictionaries"] = {}

        for language in self.startup_options["Target Languages"]:
            if language in dictionary_options:
                self.startup_options["Dictionaries"][language] = dictionary_options[
                    language
                ]

        # Accept dialog
        self.accept()

    def go_back_from_dictionary_options(self):
        self.dictionary_options_page.clear_dictionaries()
        if self.startup_options["Mode"] == "Text":
            self.reset_to_text_page()
        elif self.startup_options["Mode"] == "AVI":
            self.reset_to_avi_page()

    def get_options(self):
        return self.startup_options


class TextWidget(QWidget):
    """
    A widget for selecting source and target languages for text-based study mode.
    """

    def __init__(self) -> None:
        """
        Initialise the TextWidget, setting up the user interface components.
        """
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """
        Set up the user interface of the widget, including buttons and language selection dropdowns.
        """
        # Back button to exit
        self.back_button = QPushButton("Go back")
        back_button_layout = QHBoxLayout()
        back_button_layout.addWidget(self.back_button)

        # Source language selection
        self.source_language_label = QLabel("Choose source language (L1):")
        self.source_language_dropdown = QComboBox()
        self.source_language_dropdown.addItem("English")
        self.source_language_dropdown.setCurrentText("English")

        source_language_layout = QHBoxLayout()
        source_language_layout.addWidget(self.source_language_label)
        source_language_layout.addWidget(self.source_language_dropdown)

        # Target language selection
        self.target_language_label = QLabel("Choose target language (L2):")
        self.target_language_dropdown = QComboBox()
        self.target_language_dropdown.addItems(all_target_languages)
        self.target_language_dropdown.setCurrentText("Spanish")

        target_language_layout = QHBoxLayout()
        target_language_layout.addWidget(self.target_language_label)
        target_language_layout.addWidget(self.target_language_dropdown)

        # Confirm button
        self.confirm_button = QPushButton("Confirm")
        confirm_button_layout = QHBoxLayout()
        confirm_button_layout.addWidget(self.confirm_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(back_button_layout)
        main_layout.addLayout(source_language_layout)
        main_layout.addLayout(target_language_layout)
        main_layout.addLayout(confirm_button_layout)
        self.setLayout(main_layout)

    def get_languages(self) -> Tuple[str, str]:
        """
        Retrieve the selected source and target languages from the dropdowns.

        Returns:
            Tuple[str, str]: A tuple containing the selected source language and target language.
        """
        source_language = self.source_language_dropdown.currentText()
        target_language = self.target_language_dropdown.currentText()
        return source_language, target_language


class AVIWidget(QWidget):
    """
    A widget for configuring audiovisual input (AVI) options.
    """

    def __init__(self) -> None:
        """
        Initialise the AVIWidget, setting up the user interface components.
        """
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """
        Set up the user interface of the widget.
        """
        main_layout = QVBoxLayout()

        # Back button to exit
        self.back_button = QPushButton("Go back")
        main_layout.addWidget(self.back_button)

        # Horizontal line to separate
        main_layout.addWidget(create_separator_line())

        # Folder selection
        self.folder_label = QLabel("Choose folder:")
        self.folder_line_edit = QLineEdit()
        self.folder_line_edit.setDisabled(True)
        self.folder_button = QPushButton("Browse")
        self.folder_button.clicked.connect(self.choose_folder)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_line_edit)
        folder_layout.addWidget(self.folder_button)
        main_layout.addLayout(folder_layout)

        # Video file selection
        self.file_label = QLabel("Choose video file:")
        self.video_file_dropdown = QComboBox()
        self.video_file_dropdown.setMinimumWidth(400)
        self.video_file_dropdown.currentIndexChanged.connect(
            self.update_audio_dropdowns
        )

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.video_file_dropdown)
        main_layout.addLayout(file_layout)

        main_layout.addWidget(create_separator_line())

        # Reference language selection
        self.reference_language_subtitle_label = QLabel("Reference subtitle file:")
        self.reference_language_subtitle_dropdown = QComboBox()

        reference_language_layout = QVBoxLayout()

        reference_language_layout.addWidget(self.reference_language_subtitle_label)
        reference_language_layout.addWidget(self.reference_language_subtitle_dropdown)
        main_layout.addLayout(reference_language_layout)

        main_layout.addWidget(create_separator_line())

        # TODO: Refactor source/target lang1/target lang2 options to a function.
        # TODO: Allow adding more than 2 target languages

        # Source language selection
        self.source_language_label = QLabel("Source language (L1):")
        self.source_language_dropdown = QComboBox()
        self.source_language_dropdown.addItem("English")
        self.source_language_audio_label = QLabel("Audio:")
        self.source_language_audio_dropdown = QComboBox()
        self.source_language_subtitle_label = QLabel("Subtitle file:")
        self.source_language_subtitle_dropdown = QComboBox()

        source_language_layout = QVBoxLayout()

        source_language_layout.addWidget(self.source_language_label)
        source_language_layout.addWidget(self.source_language_dropdown)
        source_language_layout.addWidget(self.source_language_audio_label)
        source_language_layout.addWidget(self.source_language_audio_dropdown)
        source_language_layout.addWidget(self.source_language_subtitle_label)
        source_language_layout.addWidget(self.source_language_subtitle_dropdown)
        main_layout.addLayout(source_language_layout)

        main_layout.addWidget(create_separator_line())

        # Target language 1 selection
        self.target_language_1_label = QLabel("Target language 1:")
        self.target_language_1_dropdown = QComboBox()
        self.target_language_1_dropdown.addItems(all_target_languages)
        self.target_language_1_dropdown.setCurrentText("Spanish")
        self.target_language_1_audio_label = QLabel("Audio:")
        self.target_language_1_audio_dropdown = QComboBox()
        self.target_language_1_subtitle_label = QLabel("Subtitle file:")
        self.target_language_1_subtitle_dropdown = QComboBox()

        target_language_1_layout = QVBoxLayout()

        target_language_1_layout.addWidget(self.target_language_1_label)
        target_language_1_layout.addWidget(self.target_language_1_dropdown)
        target_language_1_layout.addWidget(self.target_language_1_audio_label)
        target_language_1_layout.addWidget(self.target_language_1_audio_dropdown)
        target_language_1_layout.addWidget(self.target_language_1_subtitle_label)
        target_language_1_layout.addWidget(self.target_language_1_subtitle_dropdown)
        main_layout.addLayout(target_language_1_layout)

        main_layout.addWidget(create_separator_line())

        # Target language 2 selection
        self.target_language_2_label = QLabel("Target language 2:")
        self.target_language_2_dropdown = QComboBox()
        self.target_language_2_dropdown.addItem("None")
        self.target_language_2_dropdown.addItems(all_target_languages)
        self.target_language_2_audio_label = QLabel("Audio:")
        self.target_language_2_audio_dropdown = QComboBox()
        self.target_language_2_subtitle_label = QLabel("Subtitle file:")
        self.target_language_2_subtitle_dropdown = QComboBox()

        target_language_2_layout = QVBoxLayout()

        target_language_2_layout.addWidget(self.target_language_2_label)
        target_language_2_layout.addWidget(self.target_language_2_dropdown)
        target_language_2_layout.addWidget(self.target_language_2_audio_label)
        target_language_2_layout.addWidget(self.target_language_2_audio_dropdown)
        target_language_2_layout.addWidget(self.target_language_2_subtitle_label)
        target_language_2_layout.addWidget(self.target_language_2_subtitle_dropdown)
        main_layout.addLayout(target_language_2_layout)

        main_layout.addWidget(create_separator_line())

        # Confirm button
        self.confirm_button = QPushButton("Confirm")
        confirm_button_layout = QHBoxLayout()
        confirm_button_layout.addWidget(self.confirm_button)
        main_layout.addLayout(confirm_button_layout)

        self.setLayout(main_layout)

    def choose_folder(self) -> None:
        """Opens a dialog to allow the user to choose a folder, sets the folder path, and updates the dropdowns."""
        folder = QFileDialog.getExistingDirectory(
            self, "Choose AVI Folder", LANGUAGE_LEARNING_MATERIAL_PATH
        )

        if folder == "":
            return
        folder = folder.replace("/", "\\")

        self.folder_line_edit.setText(folder)
        self.update_video_file_dropdown(folder)
        self.update_subtitle_dropdowns(folder)

    def update_video_file_dropdown(self, folder: str) -> None:
        """Updates the video file dropdown with MP4 files from the selected folder."""
        self.video_file_dropdown.clear()
        self.video_file_dropdown.addItem("None")

        folder_path = Path(folder)
        mp4_files = [file.name for file in folder_path.glob("*.mp4")]

        self.video_file_dropdown.addItems(mp4_files)

    def update_audio_dropdowns(self):
        """Updates the audio track dropdowns with audio tracks extracted from the selected video file."""
        video_file_path = self.get_video_file_path()

        try:
            audio_tracks = get_audio_tracks(video_file_path)
        except:
            audio_tracks = []

        self.source_language_audio_dropdown.clear()
        self.source_language_audio_dropdown.addItem("None")
        self.source_language_audio_dropdown.addItems(audio_tracks)

        self.target_language_1_audio_dropdown.clear()
        self.target_language_1_audio_dropdown.addItem("None")
        self.target_language_1_audio_dropdown.addItems(audio_tracks)

        self.target_language_2_audio_dropdown.clear()
        self.target_language_2_audio_dropdown.addItem("None")
        self.target_language_2_audio_dropdown.addItems(audio_tracks)

    def update_subtitle_dropdowns(self, folder):
        """Updates the subtitle file dropdowns with SRT files from the selected folder."""
        self.reference_language_subtitle_dropdown.clear()
        self.source_language_subtitle_dropdown.clear()
        self.target_language_1_subtitle_dropdown.clear()
        self.target_language_2_subtitle_dropdown.clear()

        self.reference_language_subtitle_dropdown.addItem("None")
        self.source_language_subtitle_dropdown.addItem("None")
        self.target_language_1_subtitle_dropdown.addItem("None")
        self.target_language_2_subtitle_dropdown.addItem("None")

        subtitle_files = [file.name for file in Path(folder).glob("*.srt")]

        self.reference_language_subtitle_dropdown.addItems(subtitle_files)
        self.source_language_subtitle_dropdown.addItems(subtitle_files)
        self.target_language_1_subtitle_dropdown.addItems(subtitle_files)
        self.target_language_2_subtitle_dropdown.addItems(subtitle_files)

    def get_video_file_path(self) -> str:
        """Retrieves the full path of the selected video file."""
        video_file_name = self.video_file_dropdown.currentText()
        folder = Path(self.folder_line_edit.text())
        return get_path(video_file_name, folder)

    def get_all_options(self) -> Dict[str, Any]:
        """
        Collects and returns all configured AVI options including video file, languages, audio tracks, and subtitles.

        Returns:
            options (Dict[str, Any]): A dictionary containing all the AVI options.
        """
        # TODO: Perhaps refactor this

        folder = Path(self.folder_line_edit.text())

        video_file = get_path(self.video_file_dropdown.currentText(), folder)

        source_language = self.source_language_dropdown.currentText()
        target_languages = [
            self.target_language_1_dropdown.currentText(),
            self.target_language_2_dropdown.currentText(),
        ]

        # Get audio tracks
        audio_tracks = {
            source_language: self.source_language_audio_dropdown.currentText(),
            target_languages[0]: self.target_language_1_audio_dropdown.currentText(),
            target_languages[1]: self.target_language_2_audio_dropdown.currentText(),
        }

        # Get subtitle files
        subtitle_files = {
            "Reference": get_path(
                self.reference_language_subtitle_dropdown.currentText(), folder
            ),
            source_language: get_path(
                self.source_language_subtitle_dropdown.currentText(), folder
            ),
            target_languages[0]: get_path(
                self.target_language_1_subtitle_dropdown.currentText(), folder
            ),
            target_languages[1]: get_path(
                self.target_language_2_subtitle_dropdown.currentText(), folder
            ),
        }

        # Removing values where no language was chosen
        try:
            target_languages.remove("None")
        except:
            pass

        if "None" in audio_tracks:
            audio_tracks.pop("None")
        if "None" in subtitle_files:
            subtitle_files.pop("None")

        options = {
            "Video File": video_file,
            "Source Language": source_language,
            "Target Languages": target_languages,
            "Audio Tracks": audio_tracks,
            "Subtitle Files": subtitle_files,
        }

        return options


def get_path(file_name: str, folder: Path) -> Optional[Path]:
    """Returns a Path object for the file or None if the file name is 'None'."""
    if file_name == "None" or file_name == "":
        return None
    return folder / file_name


class DictionaryChoicesWidget(QWidget):
    """
    A widget for selecting dictionaries for multiple languages using tabbed navigation.

    Attributes:
        target_to_english_dictionaries (Dict[str, Dict[str, Any]]): A dictionary where keys are language names and values
        are dictionaries containing available dictionaries for each language.
        back_button (QPushButton): Button to navigate back.
        tab_widget (QTabWidget): Tab widget to display available dictionaries for each language.
        confirm_button (QPushButton): Button to confirm the selected dictionaries.
    """

    def __init__(
        self, target_to_english_dictionaries: Dict[str, Dict[str, any]]
    ) -> None:
        """
        Initialise the DictionaryChoicesWidget.

        Args:
            target_to_english_dictionaries (Dict[str, Dict[str, Any]]): Dictionary containing available dictionaries for each language.
        """
        super().__init__()
        self.target_to_english_dictionaries = target_to_english_dictionaries
        self.init_ui()

    def init_ui(self) -> None:
        """Set up the user interface of the widget"""
        self.back_button = QPushButton("Go back")

        # Create a tab for each language
        self.tab_widget = QTabWidget()

        self.confirm_button = QPushButton("Confirm")

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.back_button)
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.confirm_button)

        self.setLayout(main_layout)

    def set_languages(self, languages: List[str]) -> None:
        """
        Set up the dictionary selection tabs based on the provided languages.

        Args:
            languages (List[str]): List of language names to create tabs for.
        """
        self.clear_dictionaries()

        for language in languages:
            if language == "English" or language == "None":
                # Don't include dictionaries for English or if a language wasn't selected
                continue

            # Create a QWidget for the tab
            tab = QWidget()

            # Create checkboxes with the available dictionaries for this language
            dictionaries = self.target_to_english_dictionaries.get(language, {})

            checkbox_layout = QVBoxLayout()

            # Simply loop through keys (i.e. dictionaries)
            for dictionary in dictionaries:
                checkbox = QCheckBox(dictionary)
                checkbox_layout.addWidget(checkbox)

            # Set the QVBoxLayout as the layout for the tab
            tab.setLayout(checkbox_layout)

            # Add the tab to the tab widget
            self.tab_widget.addTab(tab, language)

    def clear_dictionaries(self) -> None:
        self.tab_widget.clear()

    def get_dictionaries(self) -> Dict[str, List[str]]:
        """
        Retrieve the selected dictionaries for each language.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are language names and values are lists of selected dictionaries.
        """
        dictionaries = {}

        for i in range(self.tab_widget.count()):
            current_language_dictionaries = []

            tab = self.tab_widget.widget(i)
            language = self.tab_widget.tabText(i)

            for i in range(tab.layout().count()):
                checkbox = tab.layout().itemAt(i).widget()
                if checkbox.isChecked():
                    current_language_dictionaries.append(checkbox.text())

            dictionaries[language] = current_language_dictionaries

        return dictionaries


# TODO: Also refactor this, as used in several places.
def create_separator_line():
    """Create a simple separating line to place between elements in the UI."""
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line


if __name__ == "__main__":

    # # Two below to make scaling bigger on small high-res screens
    # if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
    #     QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
    #     QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    with open(
        "C:/Stuff/UniversaLearn/LangAnki/app/resources/lexilogos_old/French.json",
        "r",
    ) as f:
        french_data = json.load(f)
    with open(
        "C:/Stuff/UniversaLearn/LangAnki/app/resources/lexilogos_old/Spanish.json",
        "r",
    ) as f:
        spanish_data = json.load(f)
    target_to_english_dictionaries = {
        "French": french_data["language_to_eng"],
        "Spanish": spanish_data["language_to_eng"],
    }

    app = QApplication([])
    dialog = StartupDialog(target_to_english_dictionaries)
    if dialog.exec_() == QDialog.Accepted:
        print(dialog.startup_options)
