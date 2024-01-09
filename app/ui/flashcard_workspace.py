import shutil  # For copying audio

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
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from bs4 import BeautifulSoup  # For parsing HTML


class FlashcardWorkspace(QWidget):
    def __init__(self):
        super().__init__()

        self.fields = {}  # To track the widgets for each field of the flashcards
        self.initUI()

    def initUI(self):
        self.set_up_toolbar()
        self.set_up_fields()
        self.set_up_buttons()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.toolbar)
        main_layout.addLayout(self.fields_layout)
        main_layout.addLayout(self.button_layout)

        self.setLayout(main_layout)

    def set_up_toolbar(self):
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

    def set_up_fields(self):
        self.fields_layout = QVBoxLayout()

        # Creating choice of deck
        self.deck_label = QLabel("Deck: ")
        self.deck_dropdown = QComboBox()

        deck_box = QHBoxLayout()
        deck_box.addWidget(self.deck_label)
        deck_box.addWidget(self.deck_dropdown)
        self.fields_layout.addLayout(deck_box)

    def set_up_buttons(self):
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add\nCtrl+Enter")
        self.edit_previous_button = QPushButton("Edit Previous")
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.edit_previous_button)

    def add_field(self, field_name, field_info):
        field_type = field_info["type"]

        if field_type == "Hidden":
            widget = None
        elif field_type == "Media":
            widget_type = field_info["widget"]
            widget = self.create_media_widget(widget_type)
            self.fields_layout.addWidget(widget)
        else:
            field_box = QHBoxLayout()

            field_label = QLabel(field_name)
            widget = self.create_normal_widget(field_type)

            field_box.addWidget(field_label)
            field_box.addWidget(widget)
            self.fields_layout.addLayout(field_box)

        self.fields[field_name] = widget  # Keep track of the created widget

    def create_media_widget(self, widget_type):
        if widget_type == "ScreenshotViewer":
            return ScreenshotViewer()
        elif widget_type == "AudioViewer":
            return AudioViewer()

    def create_normal_widget(self, field_type):
        if field_type == "TextEdit":
            return QTextEdit()
        elif field_type == "LineEdit":
            return QLineEdit()
        elif field_type == "Dropdown":
            return QComboBox()
        elif field_type == "Checkbox":
            return QCheckBox()
        elif field_type == "Hidden":
            return None

    def extract_field_data(self, field_name):
        widget = self.fields[field_name]

        if widget is None:
            return ""
        elif isinstance(widget, QTextEdit):
            data = extract_textedit_data(widget)
            return data
        elif isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QCheckBox):
            return (
                "y" if widget.isChecked() else ""
            )  # Binary in Anki cards possible with a field being empty or having text

    def reset_flashcard_fields(self):
        for field_name, widget in self.fields.items():
            if widget is None:
                pass
            elif isinstance(widget, QTextEdit):
                widget.clear()  # Clear text for QTextEdit
            elif isinstance(widget, QLineEdit):
                widget.clear()  # Clear text for QLineEdit
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)  # Reset to the first item for QComboBox
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)  # Uncheck the QCheckBox
            elif isinstance(widget, ScreenshotViewer):
                widget.reset_viewer()
            elif isinstance(widget, AudioViewer):
                widget.reset_viewer()

    def swap_deck(self):
        # Get the current index of the selected option
        current_index = self.deck_dropdown.currentIndex()

        # Get the total number of options in the dropdown
        total_decks = self.deck_dropdown.count()

        # Increment the index and take the modulus to cycle through options
        next_index = (current_index + 1) % total_decks

        # Set the current index to the next index
        self.deck_dropdown.setCurrentIndex(next_index)

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


def extract_textedit_data(textedit):
    # Check if the TextEdit widget is empty
    if textedit.toPlainText().strip() == "":
        return ""

    textedit_html = textedit.toHtml()
    textedit_html = textedit_html.replace("\n", "<br>")
    textedit_data = extract_bold_formatting(textedit_html)
    return textedit_data


def extract_bold_formatting(textedit_html):
    if textedit_html == "":
        return ""

    soup = BeautifulSoup(textedit_html, "html.parser", from_encoding="utf-8")
    p = soup.find("p")

    # replacing span with strong
    for span_tag in p.find_all("span"):
        strong_tag = soup.new_tag("strong")
        strong_tag.string = span_tag.string
        span_tag.replace_with(strong_tag)

    field = "".join(str(c) for c in p.contents)
    return field


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

    def reset_viewer(self):
        self.screenshots = []
        self.update_screenshot_label()
        self.current_index = None
        self.hide_viewer

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

    def get_screenshot(self):
        if self.screenshot_label.pixmap().isNull():
            return ""
        else:
            return self.screenshot_label.pixmap().toImage()

    def save_screenshot(self, path):
        screenshot = self.get_screenshot()

        if screenshot == "":
            return

        screenshot.save(path)


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
                self.start_time_spinbox.value() - 1
            )
        )
        self.start_time_add_button = QPushButton("+1s")
        self.start_time_add_button.clicked.connect(
            lambda: self.start_time_spinbox.setValue(
                self.start_time_spinbox.value() + 1
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
            lambda: self.end_time_spinbox.setValue(self.end_time_spinbox.value() - 1)
        )
        self.end_time_add_button = QPushButton("+1s")
        self.end_time_add_button.clicked.connect(
            lambda: self.end_time_spinbox.setValue(self.end_time_spinbox.value() + 1)
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

    def reset_viewer(self):
        self.update_audio("")

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

    def get_audio_path(self):
        if self.media_player.media():
            return QUrl(self.media_player.media().canonicalUrl()).toLocalFile()
        else:
            return ""

    def save_audio(self, path):
        current_audio_path = self.get_audio_path()

        if current_audio_path == "":
            return  # No audio loaded, or an error occurred

        try:
            shutil.copy(current_audio_path, path)
        except IOError as e:
            print(f"Unable to copy file. {e}")


if __name__ == "__main__":
    # pass
    app = QApplication([])
    audio_widget = AudioViewer()
    audio_widget.show()
    app.exec_()
