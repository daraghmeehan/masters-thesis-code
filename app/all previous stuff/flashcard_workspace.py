from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QPushButton,
    QPlainTextEdit,
    QTextEdit,
    QLineEdit,
    QLabel,
    QComboBox,
    QAction,
    QToolBar,
    QSpinBox,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class FlashcardWorkspace(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.toolbar = QToolBar()

        # Create the bold action and shortcut
        self.bold_action = QAction("Bold", self)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(self.toggle_bold)

        self.toolbar.addAction(self.bold_action)

        # some styling ##??here??
        self.toolbar.setStyleSheet(
            "QToolBar { border: none; padding: 5px; background-color: #f5f5f5; }"
            "QToolButton { border: none; padding: 5px; }"
            "QToolButton:hover { background-color: #e5e5e5; }"
            "QToolButton:pressed { background-color: #d5d5d5; }"
        )

        # Creating choice of deck
        self.deck_label = QLabel("Deck: ")
        self.deck_dropdown = QComboBox()

        ## Creating fields !!make dynamic
        # Screenshots of the video
        self.screenshot_viewer = ScreenshotViewer()

        # ??
        self.audio_viewer = AudioViewer()

        self.target_label = QLabel("Target Language")
        self.target_textedit = QTextEdit()
        self.source_label = QLabel("Source Language")
        self.source_textedit = QTextEdit()

        self.answer_hint_label = QLabel("Answer Hint")
        self.answer_hint_lineedit = QLineEdit()
        self.example_sentence_label = QLabel("Example Sentence")
        self.example_sentence_textedit = QTextEdit()
        self.other_forms_label = QLabel("Other Forms")
        self.other_forms_textedit = QTextEdit()
        self.extra_info_label = QLabel("Extra Info")
        self.extra_info_textedit = QTextEdit()
        self.pronunciation_label = QLabel("Pronunciation")
        self.pronunciation_lineedit = QLineEdit()

        # Creating buttons
        self.add_button = QPushButton("Add\nCtrl+Enter")
        self.edit_previous_button = QPushButton("Edit Previous")

        ##!! should be form layout for flashcard bits!!
        # Creating layouts
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.deck_label)
        hbox1.addWidget(self.deck_dropdown)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.target_label)
        hbox2.addWidget(self.target_textedit)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.source_label)
        hbox3.addWidget(self.source_textedit)
        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.answer_hint_label)
        hbox4.addWidget(self.answer_hint_lineedit)
        hbox5 = QHBoxLayout()
        hbox5.addWidget(self.example_sentence_label)
        hbox5.addWidget(self.example_sentence_textedit)
        hbox6 = QHBoxLayout()
        hbox6.addWidget(self.other_forms_label)
        hbox6.addWidget(self.other_forms_textedit)
        hbox7 = QHBoxLayout()
        hbox7.addWidget(self.extra_info_label)
        hbox7.addWidget(self.extra_info_textedit)
        hbox8 = QHBoxLayout()
        hbox8.addWidget(self.pronunciation_label)
        hbox8.addWidget(self.pronunciation_lineedit)
        hbox9 = QHBoxLayout()
        hbox9.addWidget(self.add_button)
        hbox9.addWidget(self.edit_previous_button)

        vbox = QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)
        vbox.addLayout(hbox6)
        vbox.addLayout(hbox7)
        vbox.addLayout(hbox8)
        vbox.addLayout(hbox9)

        self.setLayout(vbox)

    def reset_flashcard_fields(self):
        self.target_textedit.setText("")
        self.source_textedit.setText("")
        self.answer_hint_lineedit.setText("")
        self.example_sentence_textedit.setText("")
        self.other_forms_textedit.setText("")
        self.extra_info_textedit.setText("")
        self.pronunciation_lineedit.setText("")

    def toggle_bold(self):
        # Get the currently focused widget
        current_widget = self.focusWidget()

        # Check if it is a QTextEdit widget
        if not isinstance(current_widget, QTextEdit):
            return

        # Get the current text cursor
        cursor = current_widget.textCursor()

        # Check if any text is selected
        if not cursor.hasSelection():
            return

        # Get the current format of the selected text (if any)
        format = cursor.charFormat()

        # Create a new format object with the appropriate font weight
        new_format = QTextCharFormat()
        new_format.setFontWeight(
            QFont.Bold if format.fontWeight() == QFont.Normal else QFont.Normal
        )

        # Apply the new formatting to the selected text
        cursor.mergeCharFormat(new_format)

    def swap_options(self):
        # Get the current index of the selected option
        current_index = self.deck_dropdown.currentIndex()

        # Swap to the other option
        if current_index == 0:
            self.deck_dropdown.setCurrentIndex(1)
        else:
            self.deck_dropdown.setCurrentIndex(0)

    def get_current_image(self):
        if self.screenshot_viewer.screenshot_label.pixmap().isNull():
            return ""
        else:
            return self.screenshot_viewer.screenshot_label.pixmap().toImage()


class ScreenshotViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.screenshots = []
        self.initUI()

    def initUI(self):
        self.current_index = None

        # Where the screenshot is held
        self.screenshot_label = QLabel(self)
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        # self.update_screenshot_label()

        prev_button = QPushButton("Prev", self)
        prev_button.clicked.connect(self.prev_screenshot)

        next_button = QPushButton("Next", self)
        next_button.clicked.connect(self.next_screenshot)

        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(next_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.screenshot_label)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.hide_viewer()  # Hide the screenshot viewer by default

    def show_viewer(self):
        self.setVisible(True)

    def hide_viewer(self):
        self.setVisible(False)

    def update_screenshots(self, screenshots):
        if screenshots == []:
            self.current_index = None
            self.hide_viewer
            return
        else:
            self.current_index = 0
            self.show_viewer()

        self.screenshots = screenshots
        self.update_screenshot_label()

    def update_screenshot_label(self):
        if self.screenshots == []:
            self.screenshot_label.setPixmap(None)
            return

        pixmap = self.screenshots[self.current_index]
        self.screenshot_label.setPixmap(pixmap)
        self.screenshot_label.setFixedSize(pixmap.size())

    def prev_screenshot(self):
        self.current_index = (self.current_index - 1) % len(self.screenshots)
        self.update_screenshot_label()

    def next_screenshot(self):
        self.current_index = (self.current_index + 1) % len(self.screenshots)
        self.update_screenshot_label()


class AudioViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.start_time_label = QLabel("Added start time")

        self.start_time_spinbox = QSpinBox()
        self.start_time_spinbox.setRange(0, 4)
        self.start_time_spinbox.setValue(0)
        self.start_time_spinbox.setButtonSymbols(2)

        start_time_value_layout = QHBoxLayout()
        start_time_value_layout.addWidget(self.start_time_label, 1)
        start_time_value_layout.addWidget(self.start_time_spinbox, 2)

        self.start_time_subtract_button = QPushButton("-1s")
        self.start_time_subtract_button.clicked.connect(
            lambda: self.start_time_spinbox.setValue(
                self.start_time_spinbox.value() - 1.0
            )
        )
        self.start_time_add_button = QPushButton("+1s")
        self.start_time_add_button.clicked.connect(
            lambda: self.start_time_spinbox.setValue(
                self.start_time_spinbox.value() + 1.0
            )
        )

        start_time_button_layout = QHBoxLayout()
        start_time_button_layout.addWidget(self.start_time_subtract_button)
        start_time_button_layout.addWidget(self.start_time_add_button)

        start_time_layout = QVBoxLayout()
        start_time_layout.addLayout(start_time_value_layout)
        start_time_layout.addLayout(start_time_button_layout)

        # create QPushButton to stop audio
        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_audio)

        # create QPushButton to play audio
        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.play_audio)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.play_button)

        self.end_time_label = QLabel("Added end time")

        self.end_time_spinbox = QSpinBox()
        self.end_time_spinbox.setRange(0, 4)
        self.end_time_spinbox.setValue(0)
        self.end_time_spinbox.setButtonSymbols(2)

        end_time_value_layout = QHBoxLayout()
        end_time_value_layout.addWidget(self.end_time_label, 1)
        end_time_value_layout.addWidget(self.end_time_spinbox, 2)

        self.end_time_subtract_button = QPushButton("-1s")
        self.end_time_subtract_button.clicked.connect(
            lambda: self.end_time_spinbox.setValue(self.end_time_spinbox.value() - 1.0)
        )
        self.end_time_add_button = QPushButton("+1s")
        self.end_time_add_button.clicked.connect(
            lambda: self.end_time_spinbox.setValue(self.end_time_spinbox.value() + 1.0)
        )

        end_time_button_layout = QHBoxLayout()
        end_time_button_layout.addWidget(self.end_time_subtract_button)
        end_time_button_layout.addWidget(self.end_time_add_button)

        end_time_layout = QVBoxLayout()
        end_time_layout.addLayout(end_time_value_layout)
        end_time_layout.addLayout(end_time_button_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(start_time_layout, 1)
        main_layout.addLayout(button_layout, 2)
        main_layout.addLayout(end_time_layout, 1)
        self.setLayout(main_layout)

        self.hide_viewer()  # Hide the audio viewer by default

        # create the QMediaPlayer object
        self.media_player = QMediaPlayer(self)

    def show_viewer(self):
        self.setVisible(True)

    def hide_viewer(self):
        self.setVisible(False)

    def update_audio(self, audio_path):
        if audio_path == "":
            self.media_player.setMedia(None)
            self.hide_viewer()

        media_content = QMediaContent(QUrl.fromLocalFile(audio_path))
        self.media_player.setMedia(media_content)

        if self.isHidden():
            self.show_viewer()

    def play_audio(self):
        self.media_player.play()

    def stop_audio(self):
        self.media_player.stop()


if __name__ == "__main__":
    # pass
    app = QApplication([])
    audio_widget = AudioViewer()
    audio_widget.show()
    app.exec_()
