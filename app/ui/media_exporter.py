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
    QFrame,
)


class MediaExporter(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        ...

        self.exit_button = QPushButton("Exit")

        # Confirm button
        self.confirm_button = QPushButton("Confirm")

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.back_button)
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.confirm_button)

        self.setLayout(main_layout)


class AVIWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # # Back button to exit
        # self.back_button = QPushButton("Go back")
        # back_button_layout = QHBoxLayout()
        # back_button_layout.addWidget(self.back_button)

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
        # folder_name = QFileDialog.getExistingDirectory(self, "Choose AVI Folder")
        folder_name = QFileDialog.getExistingDirectory(
            self, "Choose AVI Folder", LANGUAGE_LEARNING_MATERIAL_PATH
        )
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
