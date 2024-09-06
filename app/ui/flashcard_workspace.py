import shutil  # For copying audio
from typing import Optional, List
from bs4 import BeautifulSoup  # For parsing HTML

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
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
    QAbstractSpinBox,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QTextCharFormat, QFont, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class FlashcardWorkspace(QWidget):
    """
    A class representing the flashcard workspace in the application.

    Attributes:
        mode (str): The mode of the workspace, either "Text" or "AVI".
        fields (dict): A dictionary to track the widgets for each field of the flashcards.
    """

    def __init__(self, mode: str) -> None:
        """
        Initializes the FlashcardWorkspace with the given mode.

        Args:
            mode (str): The mode of the workspace, either "Text" or "AVI".
        """
        super().__init__()
        self.mode = mode
        self.fields = {}  # To track the widgets for each field of the flashcards
        self.initUI()

    def initUI(self) -> None:
        """
        Initializes the UI components of the flashcard workspace.
        """
        self.set_up_toolbar()
        self.set_up_fields()
        self.set_up_buttons()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.toolbar)
        main_layout.addLayout(self.fields_layout)
        main_layout.addLayout(self.button_layout)

        self.setLayout(main_layout)

    def set_up_toolbar(self) -> None:
        """
        Sets up the toolbar with the bold button/action, and styling.
        """
        self.toolbar = QToolBar()

        # Create the bold action and shortcut
        self.bold_action = QAction("Bold", self)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(self.toggle_bold)

        self.toolbar.addAction(self.bold_action)

        self.toolbar.setStyleSheet(
            "QToolBar { border: none; padding: 0px; background-color: #f5f5f5; }"
            "QToolButton { border: none; padding: 5px; background-color: #e5e5e5; }"
            "QToolButton:hover { background-color: #dddddd; }"
            "QToolButton:pressed { background-color: #d5d5d5; }"
        )

    def set_up_fields(self) -> None:
        """
        Sets up the flashcard field layout, with slightly different layouts for Text/AVI modes.
        """
        self.fields_layout = QVBoxLayout()

        # Creating choice of deck
        self.deck_label = QLabel("Deck: ")
        self.deck_dropdown = QComboBox()

        deck_box = QHBoxLayout()
        deck_box.addWidget(self.deck_label)
        deck_box.addWidget(self.deck_dropdown)
        self.fields_layout.addLayout(deck_box)

        self.question_text_layout = QHBoxLayout()
        self.translate_question_text_layout = QHBoxLayout()
        self.answer_text_layout = QHBoxLayout()

        if self.mode == "AVI":
            self.fields_layout.addLayout(self.question_text_layout, 3)
            self.fields_layout.addLayout(self.translate_question_text_layout, 1)
            self.fields_layout.addLayout(self.answer_text_layout, 3)

            self.checkbox_layout = QHBoxLayout()
            self.fields_layout.addLayout(self.checkbox_layout, 1)
        else:
            self.fields_layout.addLayout(self.question_text_layout, 2)
            self.fields_layout.addLayout(self.translate_question_text_layout, 1)
            self.fields_layout.addLayout(self.answer_text_layout, 2)

        # Custom question/answer layout
        question_language_label = QLabel("Question Language:")
        question_language_label.setFixedWidth(100)
        question_language_dropdown = QComboBox()
        question_text_edit = QTextEdit()

        question_language_layout = QVBoxLayout()
        question_language_layout.addWidget(
            question_language_label, 1, alignment=Qt.AlignTop
        )
        question_language_layout.addWidget(
            question_language_dropdown, 9, alignment=Qt.AlignTop
        )

        self.question_text_layout.addLayout(question_language_layout)
        self.question_text_layout.addWidget(question_text_edit)

        # For translating the question text into the answer text
        translate_question_text_label = QLabel()
        translate_question_text_label.setFixedWidth(100)
        self.translate_question_text_button = QPushButton("Translate ↓")

        self.translate_question_text_layout.addWidget(translate_question_text_label)
        self.translate_question_text_layout.addWidget(
            self.translate_question_text_button
        )

        answer_language_label = QLabel("Answer Language:")
        answer_language_label.setFixedWidth(100)
        answer_language_dropdown = QComboBox()
        answer_text_edit = QTextEdit()

        answer_language_layout = QVBoxLayout()
        answer_language_layout.addWidget(
            answer_language_label, 1, alignment=Qt.AlignTop
        )
        answer_language_layout.addWidget(
            answer_language_dropdown, 9, alignment=Qt.AlignTop
        )

        self.answer_text_layout.addLayout(answer_language_layout)
        self.answer_text_layout.addWidget(answer_text_edit)

        if self.mode == "AVI":
            # TODO: Refactor setting up AVI widgets/fields
            # Media widgets
            self.picture_layout = QVBoxLayout()
            self.audio_layout = QVBoxLayout()
            self.fields_layout.addLayout(self.picture_layout, 5)
            self.fields_layout.addLayout(self.audio_layout, 1)

            screenshot_viewer = ScreenshotViewer()
            audio_viewer = AudioViewer()

            self.picture_layout.addWidget(screenshot_viewer)
            self.audio_layout.addWidget(audio_viewer)

        # Different fields for Text/AVI mode
        if self.mode == "AVI":
            custom_fields = {
                "Question Language": question_language_dropdown,
                "Question Text": question_text_edit,
                "Answer Language": answer_language_dropdown,
                "Answer Text": answer_text_edit,
                "Picture": screenshot_viewer,
                "Audio": audio_viewer,
            }
        else:
            custom_fields = {
                "Question Language": question_language_dropdown,
                "Question Text": question_text_edit,
                "Answer Language": answer_language_dropdown,
                "Answer Text": answer_text_edit,
            }

        self.fields.update(custom_fields)

    def set_up_buttons(self):
        """
        Sets up the buttons for editing previous flashcards and saving the current flashcard.
        """
        self.button_layout = QHBoxLayout()
        self.edit_previous_button = QPushButton("Edit Previous")
        self.add_button = QPushButton("Add")  # TODO: Add shortcut "\n(Ctrl+Enter)"
        self.button_layout.addWidget(self.edit_previous_button)
        self.button_layout.addWidget(self.add_button)

    def add_field(self, field_name: str, field_info: dict) -> None:
        """
        Adds a new field to the flashcard workspace.

        Args:
            field_name (str): The name of the field.
            field_info (dict): Information about the field, including field type, and widget (if field type is for audio/pictures from AVI input).
        """
        # TODO: Refactor setting up AVI widgets/fields

        field_type = field_info["type"]

        if field_name in [
            "Question Text",
            "Question Language",
            "Answer Language",
            "Answer Text",
            "Picture",
            "Audio",
        ]:
            # Skip fields already set up
            return
        elif self.mode == "Text" and field_name in [
            "Show Picture Before?",
            "Show Audio Before?",
            "Hide Text Before?",
        ]:
            # Skip AVI fields if in Text mode
            return
        elif field_type == "Hidden":
            widget = None
        # elif field_type == "Media":
        #     widget_type = field_info["widget"]
        #     widget = self.create_media_widget(widget_type)
        #     self.fields_layout.addWidget(widget, 2)
        else:
            field_label = QLabel(field_name)
            widget = self.create_normal_widget(field_type)

            field_box = QHBoxLayout()
            field_box.addWidget(field_label)
            field_box.addWidget(widget)

            if field_type == "Checkbox":
                # field_label.setFixedWidth(150)
                self.checkbox_layout.addLayout(field_box, 1)
            else:
                field_label.setFixedWidth(80)
                self.fields_layout.addLayout(field_box, 1)

        self.fields[field_name] = widget  # Keep track of the created widget

    def create_media_widget(self, widget_type: str) -> Optional[QWidget]:
        """
        Creates a media widget based on the type provided.

        Args:
            widget_type (str): The type of the widget to create.

        Returns:
            Optional[QWidget]: The created widget or None if the type is not supported.
        """
        if widget_type == "ScreenshotViewer":
            return ScreenshotViewer()
        elif widget_type == "AudioViewer":
            return AudioViewer()

    def create_normal_widget(self, field_type: str) -> Optional[QWidget]:
        """
        Creates a normal input widget based on the type provided.

        Args:
            field_type (str): The type of the widget to create.

        Returns:
            Optional[QWidget]: The created widget or None if the type is "Hidden".
        """
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

    def extract_field_data(self, field_name: str) -> str:
        """
        Extracts the data from a given field widget.

        Args:
            field_name (str): The name of the field to extract data from.

        Returns:
            str: The extracted data from the widget as a string.
        """
        if self.mode == "Text" and field_name in [
            "Show Picture Before?",
            "Show Audio Before?",
            "Hide Text Before?",
        ]:
            # TODO: Handle this better.
            # These checkboxes aren't used in Text mode.
            return ""

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
        """
        Resets all fields in the flashcard workspace to their default state.
        """
        for widget in self.fields.values():
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

    def swap_deck(self) -> None:
        """
        Cycles to the next deck, useful for a swap deck shortcut.
        """
        # Get the index of the currently selected deck
        current_index = self.deck_dropdown.currentIndex()

        # Get the total number of options in the dropdown
        total_decks = self.deck_dropdown.count()

        # Increment the index and take the modulus to cycle through options
        next_index = (current_index + 1) % total_decks

        # Set the current index to the next index
        self.deck_dropdown.setCurrentIndex(next_index)

    def toggle_bold(self) -> None:
        """
        Toggles bold formatting for selected text in the QTextEdit fields.
        """
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


def extract_textedit_data(textedit: QTextEdit) -> str:
    """
    Extracts and formats the HTML content from a QTextEdit widget
    so it is displayed correctly when imported in Anki.

    Args:
        textedit (QTextEdit): The QTextEdit widget to extract data from.

    Returns:
        str: The formatted HTML content of the QTextEdit widget, or an empty
        string if the QTextEdit is empty.
    """
    # Check if the TextEdit widget is empty
    if textedit.toPlainText().strip() == "":
        return ""

    textedit_html = textedit.toHtml()
    textedit_html = textedit_html.replace("\n", "<br>")
    textedit_data = extract_bold_formatting(textedit_html)
    return textedit_data


def extract_bold_formatting(textedit_html: str) -> str:
    """
    Converts span tags to strong tags in the HTML content for displaying
    bold sections correctly in imported Anki flashcards.

    Args:
        textedit_html (str): The HTML content from a QTextEdit widget.

    Returns:
        str: The HTML content with span tags replaced by strong tags for bold
        formatting, or an empty string if the input is empty.
    """
    if textedit_html == "":
        return ""

    soup = BeautifulSoup(textedit_html, "html.parser")
    p = soup.find("p")

    # Replacing span tags with strong tags for bold formatting
    for span_tag in p.find_all("span"):
        strong_tag = soup.new_tag("strong")
        strong_tag.string = span_tag.string
        span_tag.replace_with(strong_tag)

    field = "".join(str(c) for c in p.contents)
    return field


class ScreenshotViewer(QWidget):
    """
    A widget for viewing and managing a list of screenshots.

    Attributes:
        screenshots (List[QPixmap]): A list to hold the screenshots as QPixmap objects.
        current_index (Optional[int]): The index of the currently displayed screenshot.
        screenshot_label (QLabel): The label widget used to display the current screenshot.
    """

    def __init__(self) -> None:
        """
        Initializes the ScreenshotViewer widget.
        """
        super().__init__()
        self.screenshots = []
        self.current_index = None
        self.initUI()

    def initUI(self) -> None:
        """
        Sets up the user interface components of the screenshot viewer.
        """
        # Where the screenshot is held
        self.screenshot_label = QLabel(self)
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        # self.screenshot_label.setSizePolicy(
        #     QSizePolicy.Expanding, QSizePolicy.Expanding
        # )

        # Previous and Next buttons
        prev_button = QPushButton("Prev", self)
        prev_button.clicked.connect(self.prev_screenshot)

        next_button = QPushButton("Next", self)
        next_button.clicked.connect(self.next_screenshot)

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(next_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.screenshot_label, alignment=Qt.AlignCenter)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.hide_viewer()  # Hide the screenshot viewer by default

    def show_viewer(self) -> None:
        self.setVisible(True)

    def hide_viewer(self) -> None:
        self.setVisible(False)

    def reset_viewer(self) -> None:
        """
        Resets the viewer, clearing all screenshots and hiding the widget.
        """
        self.screenshots = []
        self.current_index = None
        self.update_screenshot_label()
        self.hide_viewer()

    def update_screenshots(self, screenshots: List[QPixmap]) -> None:
        """
        Updates the viewer with a new set of screenshots.

        Args:
            screenshots (List[QPixmap]): A list of QPixmap objects representing the screenshots.
        """
        if screenshots == []:
            self.screenshots = []
            self.current_index = None
            self.hide_viewer()
            return

        self.screenshots = screenshots
        self.current_index = 0
        self.update_screenshot_label()
        self.show_viewer()

    def update_screenshot_label(self) -> None:
        """
        Updates the QLabel to display the current screenshot based on the index.
        """
        if self.screenshots == []:
            self.screenshot_label.clear()
            return

        pixmap = self.screenshots[self.current_index]
        self.screenshot_label.setPixmap(pixmap)
        self.screenshot_label.setFixedSize(pixmap.size())

    def prev_screenshot(self) -> None:
        """
        Moves to the previous screenshot in the list and updates the display.
        """
        if self.screenshots:
            self.current_index = (self.current_index - 1) % len(self.screenshots)
            self.update_screenshot_label()

    def next_screenshot(self) -> None:
        """
        Moves to the next screenshot in the list and updates the display.
        """
        if self.screenshots:
            self.current_index = (self.current_index + 1) % len(self.screenshots)
            self.update_screenshot_label()

    def get_screenshot(self) -> Optional[QPixmap]:
        """
        Retrieves the currently displayed screenshot as a QPixmap.

        Returns:
            Optional[QPixmap]: The currently displayed screenshot, or None if there is no screenshot.
        """
        pixmap = self.screenshot_label.pixmap()  # Get the current pixmap
        return pixmap.toImage() if pixmap and not pixmap.isNull() else None

    # TODO: Need to sort path/Path differences everywhere :(
    def save_screenshot(self, path):
        screenshot = self.get_screenshot()

        if screenshot:
            screenshot.save(str(path))

    def has_screenshots(self) -> bool:
        """
        Checks whether there are any screenshots in the viewer.

        Returns:
            bool: True if there are screenshots, otherwise False.
        """
        return bool(self.screenshots)


class AudioViewer(QWidget):
    """
    A widget that provides controls for audio playback and allows users to manage start and end times for subtitle audio.

    Attributes:
        media_player (QMediaPlayer): The media player used to handle audio playback.
        start_time_spinbox (QSpinBox): Spinbox for selecting the start time of the audio.
        end_time_spinbox (QSpinBox): Spinbox for selecting the end time of the audio.
        play_button (QPushButton): Button to start audio playback.
        stop_button (QPushButton): Button to stop audio playback.
        audio_path (str): The path of the currently loaded audio file.

    Signals:
        play_requested (pyqtSignal): Emitted when playback is requested, passing the audio file path.
        stop_requested (pyqtSignal): Emitted when the stop action is requested.
        change_audio_time (pyqtSignal): Emitted when the start or end time is changed, passing the time type (e.g., "Start Time", "End Time") and the amount to change it by.
    """

    play_requested = pyqtSignal(str)
    stop_requested = pyqtSignal()
    change_audio_time = pyqtSignal(str, int)

    def __init__(self) -> None:
        """
        Initializes the AudioViewer widget, sets up the UI, and creates the QMediaPlayer object.
        """
        super().__init__()
        self.init_ui()
        self.hide_viewer()  # Hide the audio viewer by default
        self.media_player = QMediaPlayer(self)

    def init_ui(self) -> None:
        """
        Initializes the user interface components and sets up layout.
        """
        self.create_start_time_ui()
        self.create_buttons_ui()
        self.create_end_time_ui()

        main_layout = QGridLayout()
        main_layout.addLayout(self.start_time_value_layout, 0, 0)
        main_layout.addLayout(self.start_time_edit_layout, 1, 0)
        main_layout.addWidget(self.play_button, 0, 1)
        main_layout.addWidget(self.stop_button, 1, 1)
        main_layout.addLayout(self.end_time_value_layout, 0, 2)
        main_layout.addLayout(self.end_time_edit_layout, 1, 2)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)
        main_layout.setColumnStretch(2, 1)
        self.setLayout(main_layout)

        # TODO: Actually implement these.
        # Connect the valueChanged signal of the end_time_spinbox to directly emit the change_audio_time signal
        self.end_time_spinbox.valueChanged.connect(
            lambda value: self.change_audio_time.emit("End Time", value)
        )
        self.start_time_spinbox.valueChanged.connect(
            lambda value: self.change_audio_time.emit("Start Time", value)
        )

    def create_start_time_ui(self):
        """
        Creates and sets up the user interface components for selecting the start time of the audio.
        """
        start_time_label = QLabel("Added start time")

        self.start_time_spinbox = QSpinBox()
        self.start_time_spinbox.setRange(0, 4)
        self.start_time_spinbox.setValue(0)
        self.start_time_spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)

        self.start_time_value_layout = QHBoxLayout()
        self.start_time_value_layout.addWidget(start_time_label, 1)
        self.start_time_value_layout.addWidget(self.start_time_spinbox, 2)

        start_time_subtract_button = QPushButton("-1s")
        start_time_subtract_button.clicked.connect(
            lambda: self.adjust_time(self.start_time_spinbox, -1)
        )
        start_time_add_button = QPushButton("+1s")
        start_time_add_button.clicked.connect(
            lambda: self.adjust_time(self.start_time_spinbox, 1)
        )

        self.start_time_edit_layout = QHBoxLayout()
        self.start_time_edit_layout.addWidget(start_time_subtract_button)
        self.start_time_edit_layout.addWidget(start_time_add_button)

    def create_buttons_ui(self) -> None:
        """
        Creates and sets up the user interface components for playback controls.
        """
        self.play_button = QPushButton("▶️")
        self.play_button.clicked.connect(
            lambda: self.play_requested.emit(self.get_audio_path())
        )

        self.stop_button = QPushButton("■")
        self.stop_button.clicked.connect(self.stop_requested.emit)

    # TODO: Refactor start and end time setup, as very similar.
    def create_end_time_ui(self) -> None:
        """
        Creates and sets up the user interface components for selecting the end time of the audio.
        """
        end_time_label = QLabel("Added end time")

        self.end_time_spinbox = QSpinBox()
        self.end_time_spinbox.setRange(0, 4)
        self.end_time_spinbox.setValue(0)
        self.end_time_spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)

        self.end_time_value_layout = QHBoxLayout()
        self.end_time_value_layout.addWidget(end_time_label, 1)
        self.end_time_value_layout.addWidget(self.end_time_spinbox, 2)

        end_time_subtract_button = QPushButton("-1s")
        end_time_subtract_button.clicked.connect(
            lambda: self.adjust_time(self.end_time_spinbox, -1)
        )
        end_time_add_button = QPushButton("+1s")
        end_time_add_button.clicked.connect(
            lambda: self.adjust_time(self.end_time_spinbox, 1)
        )

        self.end_time_edit_layout = QHBoxLayout()
        self.end_time_edit_layout.addWidget(end_time_subtract_button)
        self.end_time_edit_layout.addWidget(end_time_add_button)

    def adjust_time(self, spinbox: QSpinBox, delta: int) -> None:
        """
        Adjusts the value of the given spinbox by the specified delta.

        Args:
            spinbox (QSpinBox): The spinbox to adjust.
            delta (int): The amount to adjust the spinbox value by.
        """
        spinbox.setValue(spinbox.value() + delta)

    def show_viewer(self) -> None:
        self.setVisible(True)

    def hide_viewer(self) -> None:
        self.setVisible(False)

    def reset_viewer(self) -> None:
        """
        Resets the audio viewer by clearing the current audio.
        """
        self.update_audio("")

    def update_audio(self, audio_path: str) -> None:
        """
        Updates the audio path and shows/hides the viewer if given audio or not.

        Args:
            audio_path (str): The path to the audio file to load.
        """
        self.audio_path = audio_path

        if audio_path == "":
            self.hide_viewer()
            return

        if self.isHidden():
            self.show_viewer()

    def get_audio_path(self) -> str:
        return self.audio_path

    def has_audio(self) -> bool:
        return bool(self.get_audio_path())


if __name__ == "__main__":
    app = QApplication([])
    audio_widget = AudioViewer()
    audio_widget.show()
    app.exec_()
