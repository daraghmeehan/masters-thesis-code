import sys
from typing import List

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QWidget,
)

from ui.study_materials import StudyMaterials
from ui.translation_workspace import TranslationWorkspace
from ui.flashcard_workspace import FlashcardWorkspace
from ui.dictionary_lookup import DictionaryLookup


class MainWindow(QMainWindow):
    """
    The main application window of the program.

    Attributes:
        mode (str): The current mode of the application.
        languages (list): List of all languages in use in the application.
        central_widget (QWidget): The central widget of the main window.
        layout (QGridLayout): Layout manager for the central widget.
        study_materials (StudyMaterials): Widget for study materials, either saved sentences or the multilingual parallel text of AVI dialogue.
        flashcard_workspace (FlashcardWorkspace): Widget for flashcard workspace, where flashcards are edited and saved.
        translation_workspace (TranslationWorkspace): Widget for translation workspace, for translating words and phrases.
        dictionary_lookup (DictionaryLookup): Widget for dictionary lookup, for looking up words.
    """

    def __init__(self, window_title: str, mode: str, languages: List[str]) -> None:
        """
        Initialise the MainWindow.

        Args:
            window_title (str): The title of the main window.
            mode (str): The current mode of the application.
            languages (List[str]): List of languages used in the application.
        """
        super().__init__()
        self.mode = mode
        self.languages = languages
        self.initUI(window_title)

    def initUI(self, window_title: str) -> None:
        """
        Set up the user interface for the main window.

        Args:
            window_title (str): The title of the main window.
        """
        # Set the window title
        self.setWindowTitle(f"v2 - {window_title}")
        self.setGeometry(100, 100, 1000, 400)

        # Set up the central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        self.set_up_layout()
        self.set_up_tab_order()

    def set_up_layout(self):
        """Initialise and arrange the widgets of the program."""
        self.study_materials = StudyMaterials(
            mode=self.mode,
            languages=self.languages,
        )
        self.flashcard_workspace = FlashcardWorkspace(mode=self.mode)
        self.translation_workspace = TranslationWorkspace()
        self.dictionary_lookup = DictionaryLookup()

        # Row, column, number of rows, number of columns
        self.layout.addWidget(self.study_materials, 0, 0, 3, 3)
        self.layout.addWidget(self.flashcard_workspace, 0, 3, 4, 1)
        self.layout.addWidget(self.translation_workspace, 3, 0, 1, 2)
        self.layout.addWidget(self.dictionary_lookup, 3, 2, 1, 1)

        # (The grid layout acts up if you don't do this)
        for i in range(0, self.layout.columnCount()):
            self.layout.setColumnStretch(i, 1)
        for i in range(0, self.layout.rowCount()):
            self.layout.setRowStretch(i, 1)

    # TODO: Fully implement and document (in the app) shortcuts to speed up the study workflow.
    # (This might be placed elsewhere)
    # def setup_shortcuts(self):
    # """Set up keyboard shortcuts for various actions."""

    #     self.translate_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
    #     self.translate_shortcut.activated.connect(self.translate_button.click)

    #     self.copy_main_translation_shortcut = QShortcut(QKeySequence("Ctrl+1"), self)
    #     self.copy_main_translation_shortcut.activated.connect(
    #         self.main_translation_button.click
    #     )

    #     self.dictionary_lookup_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
    #     self.dictionary_lookup_shortcut.activated.connect(
    #         self.dictionary_lookup_lineedit.setFocus
    #     )
    #     self.dictionary_lookup_shortcut.activated.connect(
    #         self.set_dictionary_lookup_with_paste
    #     )

    #     self.add_flashcard_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
    #     self.add_flashcard_shortcut.activated.connect(self.add_flashcard)

    def set_up_tab_order(self):
        # TODO: Create a logical tab order to go between various sections of the UI.
        # Note: will be different between modes
        # self.setTabOrder(widget1, widget2)
        # self.setTabOrder(widget2, widget3)
        pass

    # TODO: Set up all points at which 'enter' can be pressed for different actions.
    # Perhaps should be in dictionary_lookup file itself if only one??
    def setup_all_enter_key_signals(self):
        #     self.substring_search_lineedit.returnPressed.connect(
        #         self.search_substring_button.click
        #     )

        #     self.line_number_lineedit.returnPressed.connect(
        #         self.confirm_line_number_button.click
        #     )

        self.dictionary_lookup.dictionary_lookup_lineedit.returnPressed.connect(
            self.dictionary_lookup.search_button.click
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
