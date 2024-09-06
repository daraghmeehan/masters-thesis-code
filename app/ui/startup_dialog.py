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
)

import os

import json
import ffmpeg

all_languages = [
    "Dutch",
    "German",
    "English",
    "French",
    "Italian",
    "Portuguese",
    "Spanish",
]


def get_audio_streams(filename):
    """Get a list of audio stream names from a video file"""
    streams = ffmpeg.probe(filename)["streams"]
    audio_streams = [
        s["tags"]["language"] for s in streams if s["codec_type"] == "audio"
    ]
    return audio_streams


class StartupDialog(QDialog):
    def __init__(self, tl_to_english_dictionaries):
        super().__init__()
        self.tl_to_english_dictionaries = tl_to_english_dictionaries
        self.startup_options = {"Mode": None}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Startup Dialog")

        # Create a stacked widget to hold the different pages of the dialog
        self.stacked_widget = QStackedWidget()
        self.choose_mode_page = QWidget()
        self.text_options_page = TextWidget()
        self.avi_options_page = AVIWidget()
        self.dictionary_options_page = DictionaryChoicesWidget(
            self.tl_to_english_dictionaries
        )
        self.stacked_widget.addWidget(self.choose_mode_page)
        self.stacked_widget.addWidget(self.text_options_page)
        self.stacked_widget.addWidget(self.avi_options_page)
        self.stacked_widget.addWidget(self.dictionary_options_page)

        # Choose mode page
        self.mode_label = QLabel("Choose a study mode:")
        self.text_button = QPushButton("Text (Basic Mode)")
        self.avi_button = QPushButton("Audiovisual Input")
        self.mode_layout = QVBoxLayout()
        self.mode_layout.addWidget(self.mode_label)
        self.mode_layout.addWidget(self.text_button)
        self.mode_layout.addWidget(self.avi_button)
        self.choose_mode_page.setLayout(self.mode_layout)

        ## Connecting signals and slots

        # Connecting buttons on choose mode page
        self.text_button.clicked.connect(self.text_mode_selected)
        self.avi_button.clicked.connect(self.avi_mode_selected)

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

    def reset_to_mode_page(self):
        self.startup_options = {"Mode": None}  # remove all saved options
        self.show_mode_page()

    def reset_to_text_page(self):
        self.startup_options = {"Mode": "Text"}
        self.show_text_page()

    def reset_to_avi_page(self):
        self.startup_options = {"Mode": "AVI"}
        self.show_avi_page()

    def show_mode_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_text_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_avi_page(self):
        self.stacked_widget.setCurrentIndex(2)

    def show_dictionary_page(self):
        self.stacked_widget.setCurrentIndex(3)

    def text_mode_selected(self):
        self.startup_options["Mode"] = "Text"
        self.show_text_page()

    def avi_mode_selected(self):
        self.startup_options["Mode"] = "AVI"
        self.show_avi_page()

    def text_options_confirmed(self):
        source_language, target_language = self.text_options_page.get_languages()
        self.startup_options["Source Language"] = source_language
        self.startup_options["Target Languages"] = [target_language]
        self.dictionary_options_page.set_languages([target_language])
        self.show_dictionary_page()

    def avi_options_confirmed(self):
        avi_options = self.avi_options_page.get_all_options()
        if avi_options["Video File"] == "" or avi_options["Video File"] == "None":
            # Don't allow confirming if no video has been chosen
            return

        self.startup_options.update(avi_options)

        languages = self.startup_options["Target Languages"]

        self.dictionary_options_page.set_languages(languages)
        self.show_dictionary_page()

    def dictionary_options_confirmed(self):
        dictionary_options = self.dictionary_options_page.get_dictionaries()

        self.startup_options["Dictionaries"] = {}

        for language in self.startup_options["Target Languages"]:
            self.startup_options["Dictionaries"][language] = dictionary_options[
                language
            ]

        # print(f"\nAll options:\n{self.startup_options}")

        # accept dialog
        self.accept()

    def go_back_from_dictionary_options(self):
        self.dictionary_options_page.clear_dictionaries()
        if self.startup_options["Mode"] == "Text":
            self.reset_to_text_page()
        elif self.startup_options["Mode"] == "AVI":
            self.reset_to_avi_page()

    def get_options(self):
        return self.startup_options


##!! unused!!
def choose_file(mode):
    """
    Function to open a file dialog and return the selected file's path.
    Returns an empty string if no file is selected.
    If mode is "AVI", the function selects a folder instead of a file.
    """
    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog

    if mode == "Text":
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Text File",
            "",
            "Text Files (*.txt);;All Files (*)",
            options=options,
        )
    elif mode == "AVI":
        file_path = QFileDialog.getExistingDirectory(
            None, "Select AVI Folder", "", options=options
        )
    else:
        raise ValueError(f"Invalid mode: {mode}")

    return file_path


class TextWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Back button to exit
        self.back_button = QPushButton("Go back")
        back_button_layout = QHBoxLayout()
        back_button_layout.addWidget(self.back_button)

        # Source language selection
        self.source_language_label = QLabel("Select source language:")
        self.source_language_dropdown = QComboBox()
        self.source_language_dropdown.addItem("English")
        self.source_language_dropdown.setCurrentText("English")

        source_language_layout = QHBoxLayout()
        source_language_layout.addWidget(self.source_language_label)
        source_language_layout.addWidget(self.source_language_dropdown)

        # Target language selection
        self.target_language_label = QLabel("Select target language:")
        self.target_language_dropdown = QComboBox()
        self.target_language_dropdown.addItems(all_languages)
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

    def get_languages(self):
        source_language = self.source_language_dropdown.currentText()
        target_language = self.target_language_dropdown.currentText()
        return source_language, target_language


class AVIWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Back button to exit
        self.back_button = QPushButton("Go back")
        back_button_layout = QHBoxLayout()
        back_button_layout.addWidget(self.back_button)

        # Horizontal line to separate
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

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

        # Horizontal line to separate
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)

        # Source language selection
        self.source_language_label = QLabel("Source Language:")
        self.source_language_dropdown = QComboBox()
        # self.source_language_dropdown.addItems(all_languages)
        self.source_language_dropdown.addItem("English")
        self.source_language_dropdown.setCurrentText("English")
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

        # Horizontal line to separate
        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)

        # Target language 1 selection
        self.target_language_1_label = QLabel("Target Language 1:")
        self.target_language_1_dropdown = QComboBox()
        self.target_language_1_dropdown.addItems(all_languages)
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

        # Horizontal line to separate
        line4 = QFrame()
        line4.setFrameShape(QFrame.HLine)
        line4.setFrameShadow(QFrame.Sunken)

        # Target language 2 selection
        self.target_language_2_label = QLabel("Target Language 2:")
        self.target_language_2_dropdown = QComboBox()
        self.target_language_2_dropdown.addItem("None")
        self.target_language_2_dropdown.addItems(all_languages)
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

        # Horizontal line to separate
        line5 = QFrame()
        line5.setFrameShape(QFrame.HLine)
        line5.setFrameShadow(QFrame.Sunken)

        # Confirm button
        self.confirm_button = QPushButton("Confirm")
        confirm_button_layout = QHBoxLayout()
        confirm_button_layout.addWidget(self.confirm_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(back_button_layout)
        main_layout.addWidget(line1)
        main_layout.addLayout(folder_layout)
        main_layout.addLayout(file_layout)
        main_layout.addWidget(line2)
        main_layout.addLayout(source_language_layout)
        main_layout.addWidget(line3)
        main_layout.addLayout(target_language_1_layout)
        main_layout.addWidget(line4)
        main_layout.addLayout(target_language_2_layout)
        main_layout.addWidget(line5)
        main_layout.addLayout(confirm_button_layout)
        self.setLayout(main_layout)

    def choose_folder(self):
        folder_name = QFileDialog.getExistingDirectory(self, "Choose AVI Folder")
        if folder_name == "":
            return
        folder_name = folder_name.replace("/", "\\")
        self.folder_line_edit.setText(folder_name)
        self.update_video_file_dropdown(folder_name)
        self.update_subtitle_dropdowns(folder_name)

    def update_video_file_dropdown(self, folder_name):
        self.video_file_dropdown.clear()
        self.video_file_dropdown.addItem("None")
        mp4_files = []
        for file_name in os.listdir(folder_name):
            if file_name.endswith(".mp4"):
                mp4_files.append(file_name)
        self.video_file_dropdown.addItems(mp4_files)

    def update_audio_dropdowns(self):
        video_file_path = self.get_video_file_path()

        try:
            audio_streams = get_audio_streams(video_file_path)
        except:
            audio_streams = []

        self.source_language_audio_dropdown.clear()
        self.source_language_audio_dropdown.addItem("None")
        self.source_language_audio_dropdown.addItems(audio_streams)

        self.target_language_1_audio_dropdown.clear()
        self.target_language_1_audio_dropdown.addItem("None")
        self.target_language_1_audio_dropdown.addItems(audio_streams)

        self.target_language_2_audio_dropdown.clear()
        self.target_language_2_audio_dropdown.addItem("None")
        self.target_language_2_audio_dropdown.addItems(audio_streams)

    def update_subtitle_dropdowns(self, folder_name):
        self.source_language_subtitle_dropdown.clear()
        self.target_language_1_subtitle_dropdown.clear()
        self.target_language_2_subtitle_dropdown.clear()

        self.source_language_subtitle_dropdown.addItem("None")
        self.target_language_1_subtitle_dropdown.addItem("None")
        self.target_language_2_subtitle_dropdown.addItem("None")

        subtitle_files = []
        for file_name in os.listdir(folder_name):
            if file_name.endswith(".srt"):
                subtitle_files.append(file_name)

        self.source_language_subtitle_dropdown.addItems(subtitle_files)
        self.target_language_1_subtitle_dropdown.addItems(subtitle_files)
        self.target_language_2_subtitle_dropdown.addItems(subtitle_files)

    def get_video_file_path(self):
        video_file_name = self.video_file_dropdown.currentText()
        folder_name = self.folder_line_edit.text()
        video_file_path = os.path.join(folder_name, video_file_name)
        return video_file_path

    def get_all_options(self):
        if self.video_file_dropdown.currentText() == "None":
            video_file = "None"
        else:
            video_file = self.get_video_file_path()

        source_language = self.source_language_dropdown.currentText()
        target_languages = [
            self.target_language_1_dropdown.currentText(),
            self.target_language_2_dropdown.currentText(),
        ]

        audio_tracks = {}
        subtitle_files = {}

        folder_name = self.folder_line_edit.text()

        source_language_audio_track = self.source_language_audio_dropdown.currentText()
        target_language_1_audio_track = (
            self.target_language_1_audio_dropdown.currentText()
        )
        target_language_2_audio_track = (
            self.target_language_2_audio_dropdown.currentText()
        )

        audio_tracks[source_language] = source_language_audio_track
        audio_tracks[target_languages[0]] = target_language_1_audio_track
        audio_tracks[target_languages[1]] = target_language_2_audio_track

        source_language_subtitles_file = (
            self.source_language_subtitle_dropdown.currentText()
        )
        if source_language_subtitles_file != "None":
            source_language_subtitles_file = os.path.join(
                folder_name, source_language_subtitles_file
            )
        target_language_1_subtitles_file = (
            self.target_language_1_subtitle_dropdown.currentText()
        )
        if target_language_1_subtitles_file != "None":
            target_language_1_subtitles_file = os.path.join(
                folder_name, target_language_1_subtitles_file
            )
        target_language_2_subtitles_file = (
            self.target_language_2_subtitle_dropdown.currentText()
        )
        if target_language_2_subtitles_file != "None":
            target_language_2_subtitles_file = os.path.join(
                folder_name, target_language_2_subtitles_file
            )

        subtitle_files[source_language] = source_language_subtitles_file
        subtitle_files[target_languages[0]] = target_language_1_subtitles_file
        subtitle_files[target_languages[1]] = target_language_2_subtitles_file

        options = {
            "Video File": video_file,
            "Source Language": source_language,
            "Target Languages": target_languages,
            "Audio Tracks": audio_tracks,
            "Subtitle Files": subtitle_files,
        }

        return options


class DictionaryChoicesWidget(QWidget):
    def __init__(self, tl_to_english_dictionaries):
        super().__init__()

        self.tl_to_english_dictionaries = tl_to_english_dictionaries
        self.init_ui()

    def init_ui(self):
        self.back_button = QPushButton("Go back")

        # Create a tab for each language
        self.tab_widget = QTabWidget()

        # Confirm button
        self.confirm_button = QPushButton("Confirm")

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.back_button)
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.confirm_button)

        self.setLayout(main_layout)

    def set_languages(self, languages):
        self.clear_dictionaries()

        for language in languages:
            if language == "English" or language == "None":
                # don't include dictionaries for English or if a language wasn't selected
                continue

            # Create a QWidget for the tab
            tab = QWidget()

            # Create checkboxes with the available dictionaries for this language
            dictionaries = self.tl_to_english_dictionaries[language]

            checkbox_layout = QVBoxLayout()
            for dictionary in dictionaries:
                checkbox = QCheckBox(dictionary)
                checkbox_layout.addWidget(checkbox)

            # Set the QVBoxLayout as the layout for the tab
            tab.setLayout(checkbox_layout)

            # Add the tab to the tab widget
            self.tab_widget.addTab(tab, language)

    def clear_dictionaries(self):
        self.tab_widget.clear()

    def get_dictionaries(self):
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


if __name__ == "__main__":
    with open(
        "C:/Stuff/UniversaLearn/LanguageRepo/LangAnki/Lexilogos/json_ready_march_23/english_data/French.json",
        "r",
    ) as f:
        french_data = json.load(f)
    with open(
        "C:/Stuff/UniversaLearn/LanguageRepo/LangAnki/Lexilogos/json_ready_march_23/english_data/Spanish.json",
        "r",
    ) as f:
        spanish_data = json.load(f)
    tl_to_english_dictionaries = {
        "French": french_data["language_to_eng"],
        "Spanish": spanish_data["language_to_eng"],
    }

    app = QApplication([])
    dialog = StartupDialog(tl_to_english_dictionaries)
    if dialog.exec_() == QDialog.Accepted:
        print(dialog.mode_dict)
