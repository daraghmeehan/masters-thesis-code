import os

import ffmpeg
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QToolBar,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QLabel,
    QComboBox,
    QCheckBox,
    QAction,
    QSpinBox,
    QDoubleSpinBox,
    QFrame,
    QFileDialog,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
    QRadioButton,
    QButtonGroup,
)
from PyQt5.QtCore import Qt, QLocale


# Two below to make scaling bigger on small high-res screens
if hasattr(Qt, "AA_EnableHighDpiScaling"):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, "AA_UseHighDpiPixmaps"):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


FIXED_X_BUTTON_WIDTH = 18

LANGUAGE_LEARNING_MATERIAL_PATH = (
    r"C:\Stuff\UniversaLearn\LanguageRepo\Language Learning Material"
)

sample_startup_options = {
    "Mode": "AVI",
    "Video File": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.mp4",
    "Source Language": "English",
    "Target Languages": [
        "Spanish",
        "Dutch",
        "French",
        "Japanese",
        # "Czech",
        # "Polish",
        # "Indonesian",
        # "Portuguese",
        # "Swedish",
        # "Italian",
        # "Turkish",
        # "Chinese",
    ],
    "Audio Tracks": {
        "English": "None",
        "Spanish": "None",
        "Dutch": "None",
        # "French": "None",
        # "Japanese": "None",
        # "Czech": "None",
        # "Polish": "None",
        # "Indonesian": "None",
        # "Portuguese": "None",
        # "Swedish": "None",
        # "Italian": "None",
        # "Turkish": "None",
        # "Chinese": "None",
    },
    "Subtitle Files": {
        "Reference": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.en.srt",
        # "English": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.en.srt",
        # "Spanish": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.es.srt",
        # "Dutch": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.nl.srt",
        # "French": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.fr.srt",
        # "Japanese": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.ja.srt",
        # "Czech": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.cs.srt",
        # "Polish": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.pl.srt",
        # "Indonesian": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.id.srt",
        # "Portuguese": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.pt.srt",
        # "Swedish": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.sv.srt",
        # "Italian": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.it.srt",
        # "Turkish": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.tr.srt",
        # "Chinese": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.zh-Hans.srt",
    },
}


def get_audio_tracks(filename):
    """Get a list of audio stream names from a video file"""
    tracks = ffmpeg.probe(filename)["streams"]
    audio_tracks = [s["tags"]["language"] for s in tracks if s["codec_type"] == "audio"]
    return audio_tracks


def create_separator_line():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line


class MediaExporter(QWidget):
    def __init__(self):
        super().__init__()

        self.audio_tracks = []
        self.language_rows = []  # Keep track of language row widgets
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Media Exporter")
        main_layout = QVBoxLayout()

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
        self.video_file_label = QLabel("Choose video file:")
        self.video_file_dropdown = QComboBox()
        self.video_file_dropdown.setMinimumWidth(400)
        self.video_file_dropdown.currentIndexChanged.connect(self.update_audio_tracks)

        video_file_layout = QHBoxLayout()
        video_file_layout.addWidget(self.video_file_label)
        video_file_layout.addWidget(self.video_file_dropdown)
        main_layout.addLayout(video_file_layout)

        # Reference subtitle file selection
        self.subtitle_file_label = QLabel("Choose reference subtitle file:")
        self.subtitle_file_dropdown = QComboBox()
        self.subtitle_file_dropdown.setMinimumWidth(400)

        subtitle_file_layout = QHBoxLayout()
        subtitle_file_layout.addWidget(self.subtitle_file_label)
        subtitle_file_layout.addWidget(self.subtitle_file_dropdown)
        main_layout.addLayout(subtitle_file_layout)

        main_layout.addWidget(create_separator_line())

        export_options_layout = QVBoxLayout()

        # Choosing subtitle padding
        subtitle_padding_layout = QHBoxLayout()
        subtitle_padding_label = QLabel("Subtitle padding (seconds): ")
        self.subtitle_padding = QDoubleSpinBox()
        self.subtitle_padding.setDecimals(1)
        self.subtitle_padding.setLocale(
            QLocale(QLocale.English, QLocale.Ireland)
        )  # Set the locale to use a period as decimal separator
        self.subtitle_padding.setRange(0, 10)
        self.subtitle_padding.setSingleStep(0.5)
        self.subtitle_padding.setValue(1)
        subtitle_padding_layout.addWidget(subtitle_padding_label)
        subtitle_padding_layout.addWidget(self.subtitle_padding)
        export_options_layout.addLayout(subtitle_padding_layout)

        # Segmenting
        segmenting_layout = QHBoxLayout()
        segmenting_layout.setContentsMargins(0, 0, 0, 0)
        segmenting_layout.setSpacing(0)

        segments_label = QLabel("Segmenting: ")

        self.segmenting_button_group = QButtonGroup()

        self.no_segmenting_radio = QRadioButton("No")
        self.yes_segmenting_radio = QRadioButton("Yes")

        self.segmenting_button_group.addButton(self.no_segmenting_radio, 0)
        self.segmenting_button_group.addButton(self.yes_segmenting_radio, 1)
        self.no_segmenting_radio.setChecked(True)

        self.segments_time_label = QLabel("Segment length (seconds): ")
        self.segments_time_label.setEnabled(False)

        self.segments_time = QSpinBox()
        self.segments_time.setEnabled(False)
        self.segments_time.setMinimum(0)
        self.segments_time.setMaximum(10800)  # Maximum of 3 hours
        self.segments_time.setSingleStep(1)
        self.segments_time.setValue(15)

        segmenting_layout.addWidget(segments_label, 2)
        segmenting_layout.addWidget(self.no_segmenting_radio, 1)
        segmenting_layout.addWidget(self.yes_segmenting_radio, 1)
        segmenting_layout.addWidget(self.segments_time_label, 2)
        segmenting_layout.addWidget(self.segments_time, 2)

        export_options_layout.addLayout(segmenting_layout)

        self.no_segmenting_radio.toggled.connect(self.no_segmenting_radio_clicked)
        self.yes_segmenting_radio.toggled.connect(self.yes_segmenting_radio_clicked)

        # Interleaving
        self.interleaving_layout = QHBoxLayout()
        self.interleaving_layout.setContentsMargins(0, 0, 0, 0)
        self.interleaving_layout.setSpacing(0)

        interleaving_label = QLabel("Interleaving: ")

        self.interleaving_button_group = QButtonGroup()

        self.no_interleaving_radio = QRadioButton("No")
        self.yes_interleaving_radio = QRadioButton("Yes")

        self.interleaving_button_group.addButton(self.no_interleaving_radio, 0)
        self.interleaving_button_group.addButton(self.yes_interleaving_radio, 1)
        self.no_interleaving_radio.setChecked(True)

        self.interleaved_segments_checkbox = QCheckBox("Combine interleaved segments?")
        self.interleaved_segments_checkbox.setEnabled(False)

        self.interleaving_layout.addWidget(interleaving_label, 2)
        self.interleaving_layout.addWidget(self.no_interleaving_radio, 1)
        self.interleaving_layout.addWidget(self.yes_interleaving_radio, 1)
        self.interleaving_layout.addWidget(self.interleaved_segments_checkbox, 4)

        self.no_interleaving_radio.setEnabled(False)
        self.yes_interleaving_radio.setEnabled(False)

        export_options_layout.addLayout(self.interleaving_layout)

        self.no_interleaving_radio.toggled.connect(self.no_interleaving_radio_clicked)
        self.yes_interleaving_radio.toggled.connect(self.yes_interleaving_radio_clicked)

        # Combining files or not
        file_options_layout = QHBoxLayout()
        file_options_layout.setContentsMargins(0, 0, 0, 0)  # Set margins
        file_options_layout.setSpacing(0)  # Set spacing between widgets

        self.file_options_button_group = QButtonGroup()

        self.separate_files_radio = QRadioButton("Separate files (shuffle-friendly)")
        self.all_combined_radio = QRadioButton("Combine everything (create one file)")

        self.file_options_button_group.addButton(self.separate_files_radio, 0)
        self.file_options_button_group.addButton(self.all_combined_radio, 1)
        self.all_combined_radio.setChecked(True)

        file_options_layout.addWidget(self.separate_files_radio, 1)
        file_options_layout.addWidget(self.all_combined_radio, 1)

        self.separate_files_radio.setChecked(True)

        export_options_layout.addLayout(file_options_layout)

        main_layout.addLayout(export_options_layout)

        # Container widget for language rows and button
        language_rows_container = QWidget()
        self.language_rows_layout = QVBoxLayout(language_rows_container)
        self.language_rows_layout.setAlignment(Qt.AlignTop)

        # Scroll area for the container
        languages_scroll_area = QScrollArea()
        languages_scroll_area.setWidgetResizable(True)
        languages_scroll_area.setWidget(language_rows_container)
        main_layout.addWidget(languages_scroll_area)

        # Header for language rows
        header_layout = QHBoxLayout()
        audio_track_label = QLabel("Audio Track")
        audio_track_label.setAlignment(Qt.AlignCenter)
        speed_label = QLabel("Speed")
        speed_label.setAlignment(Qt.AlignCenter)
        font = audio_track_label.font()
        font.setBold(True)
        audio_track_label.setFont(font)
        speed_label.setFont(font)
        header_layout.addWidget(audio_track_label)
        header_layout.addWidget(speed_label)
        right_padding = QWidget()
        right_padding.setFixedWidth(FIXED_X_BUTTON_WIDTH)
        header_layout.addWidget(right_padding)
        self.language_rows_layout.addLayout(header_layout)

        ## make other padding like this!!
        spacer = QSpacerItem(
            20,
            40,
            QSizePolicy.Minimum,
            QSizePolicy.Expanding,
        )
        self.language_rows_layout.addItem(spacer)

        # Add Language Button
        self.add_language_button = QPushButton("Add Language")
        self.add_language_button.clicked.connect(self.add_language_row)
        self.language_rows_layout.addWidget(self.add_language_button)

        bottom_buttons_layout = QHBoxLayout()
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(lambda x: None)
        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self.confirm_options)
        bottom_buttons_layout.addWidget(exit_button)
        bottom_buttons_layout.addWidget(confirm_button)
        main_layout.addLayout(bottom_buttons_layout)

        self.setLayout(main_layout)
        self.resize(300, 490)

    def choose_folder(self):
        # folder_name = QFileDialog.getExistingDirectory(self, "Choose AVI Folder")
        folder_name = QFileDialog.getExistingDirectory(
            self, "Choose AVI Folder", LANGUAGE_LEARNING_MATERIAL_PATH
        )
        if folder_name == "":
            return
        folder_name = folder_name.replace("/", "\\")
        self.folder_line_edit.setText(folder_name)
        self.update_video_file_dropdown(folder_name)
        self.update_subtitle_file_dropdown(folder_name)

    def update_video_file_dropdown(self, folder_name):
        self.video_file_dropdown.clear()
        mp4_files = []
        for file_name in os.listdir(folder_name):
            if file_name.endswith(".mp4"):
                mp4_files.append(file_name)
        self.video_file_dropdown.addItems(mp4_files)

    def update_subtitle_file_dropdown(self, folder_name):
        self.subtitle_file_dropdown.clear()

        subtitle_files = []
        for file_name in os.listdir(folder_name):
            if file_name.endswith(".srt"):
                subtitle_files.append(file_name)

        self.subtitle_file_dropdown.addItems(subtitle_files)

    def get_video_file_path(self):
        video_file_name = self.video_file_dropdown.currentText()
        folder_name = self.folder_line_edit.text()
        video_file_path = os.path.join(folder_name, video_file_name)
        return video_file_path

    def update_audio_tracks(self):
        video_file_path = self.get_video_file_path()

        try:
            self.audio_tracks = get_audio_tracks(video_file_path)
        except Exception as e:
            self.audio_tracks = []

        # Set audio tracks for all language rows
        for row in self.language_rows:
            row.set_audio_tracks(self.audio_tracks)

    def update_reference_subs(self, folder_name):
        subtitle_files = []
        for file_name in os.listdir(folder_name):
            if file_name.endswith(".srt"):
                subtitle_files.append(file_name)

        self.reference_subtitles_dropdown.addItems(subtitle_files)

    def no_segmenting_radio_clicked(self):
        self.segments_time_label.setEnabled(False)
        self.segments_time.setEnabled(False)

        if self.yes_interleaving_radio.isChecked():
            self.no_interleaving_radio.setChecked(True)

        self.no_interleaving_radio.setEnabled(False)
        self.yes_interleaving_radio.setEnabled(False)

    def yes_segmenting_radio_clicked(self):
        self.segments_time_label.setEnabled(True)
        self.segments_time.setEnabled(True)
        self.no_interleaving_radio.setEnabled(True)
        self.yes_interleaving_radio.setEnabled(True)

    def no_interleaving_radio_clicked(self):
        self.interleaved_segments_checkbox.setChecked(False)
        self.interleaved_segments_checkbox.setEnabled(False)
        self.separate_files_radio.setChecked(True)

    def yes_interleaving_radio_clicked(self):
        self.interleaved_segments_checkbox.setEnabled(True)

    def update_interleaving_time_state(self):
        if self.interleaved_radio.isChecked() or self.segmented_radio.isChecked():
            self.interleaving_time.setEnabled(True)
        else:
            self.interleaving_time.setEnabled(False)

    def add_language_row(self):
        new_row = self.LanguageRowWidget(self.audio_tracks)
        self.language_rows_layout.insertWidget(
            self.language_rows_layout.count() - 2, new_row
        )
        self.language_rows.append(new_row)
        new_row.delete_button.clicked.connect(lambda: self.remove_language_row(new_row))

    def remove_language_row(self, row_widget):
        # Remove the row widget from the layout and the list
        self.language_rows.remove(row_widget)
        row_widget.deleteLater()

    def confirm_options(self):
        options = [row.get_options() for row in self.language_rows]
        print(options)

    class LanguageRowWidget(QWidget):
        def __init__(self, audio_tracks):
            super().__init__()
            self.initUI(audio_tracks)

        def initUI(self, audio_tracks):
            # Audio Track Dropdown
            self.audio_track_dropdown = QComboBox()
            self.audio_track_dropdown.addItems(
                audio_tracks
            )  # Populate with available audio tracks

            # Speed SpinBox
            self.speed_spinbox = QDoubleSpinBox()
            self.speed_spinbox.setLocale(
                QLocale(QLocale.English, QLocale.Ireland)
            )  # Set the locale to use a period as decimal separator
            self.speed_spinbox.setRange(0.1, 10.0)
            self.speed_spinbox.setSingleStep(0.1)
            self.speed_spinbox.setValue(1.0)  # Default speed

            # Delete Button
            self.delete_button = QPushButton("X")
            self.delete_button.setFixedSize(FIXED_X_BUTTON_WIDTH, FIXED_X_BUTTON_WIDTH)
            self.delete_button.setStyleSheet(
                "background-color: rgb(255, 0, 0); color: white; border-radius: 12px; font-weight: bold;"
            )
            self.delete_button.clicked.connect(self.deleteRow)

            # Layout
            layout = QHBoxLayout()
            layout.addWidget(self.audio_track_dropdown)
            layout.addWidget(self.speed_spinbox)
            layout.addWidget(self.delete_button)

            self.setLayout(layout)

        def set_audio_tracks(self, audio_tracks):
            self.audio_track_dropdown.clear()
            self.audio_track_dropdown.addItems(audio_tracks)

        def get_options(self):
            return self.audio_track_dropdown.currentText(), self.speed_spinbox.value()

        def deleteRow(self):
            self.deleteLater()


def main():
    app = QApplication([])
    avi_widget = MediaExporter()
    avi_widget.show()
    app.exec_()


if __name__ == "__main__":
    main()
