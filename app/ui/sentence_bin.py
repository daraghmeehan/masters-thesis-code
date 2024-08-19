import sys

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QAction,
    QShortcut,
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSignal, Qt


class SentenceBin(QMainWindow):
    """
    A QMainWindow that allows the user to input, modify, and save sentences.

    Signals:
        sentence_added_signal (pyqtSignal): Emitted when a sentence is saved.
    """

    sentence_added_signal = pyqtSignal(str)
    # TODO: Future improvement to SentenceBin where it is handled inside View code, e.g. with close_signal = pyqtSignal()

    def __init__(self) -> None:
        """Initialises the SentenceBin window."""
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """Sets up the user interface of the SentenceBin."""
        self.setWindowTitle("Sentence Bin")

        # Create the main window layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.setLayout(self.layout)

        self.sentence_text_edit = QPlainTextEdit(self)
        self.layout.addWidget(self.sentence_text_edit)

        # Create a button to remove new lines
        self.remove_new_lines_button = QPushButton("Remove New Lines (Ctrl+N)", self)
        self.remove_new_lines_button.clicked.connect(self.remove_new_lines)
        self.layout.addWidget(self.remove_new_lines_button)

        # Shortcut for removing new lines
        self.remove_new_lines_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.remove_new_lines_shortcut.activated.connect(self.remove_new_lines)

        # Create a button to save the sentence
        self.save_button = QPushButton("Save Sentence (Ctrl+Enter)", self)
        self.save_button.clicked.connect(self.save_sentence)
        self.layout.addWidget(self.save_button)

        # Shortcut for saving the sentence
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.save_shortcut.activated.connect(self.save_sentence)

        # Close the sentence bin when ESC is pressed and the widget is in focus
        self.close_action = QAction(self)
        self.close_action.setShortcut(QKeySequence(Qt.Key_Escape))
        self.close_action.triggered.connect(self.close)

        # Add the QAction to the window
        self.addAction(self.close_action)

    def remove_new_lines(self) -> None:
        """Removes new lines and excessive spaces from the text in the editor."""
        sentence = self.sentence_text_edit.toPlainText()
        sentence = sentence.replace("\n", " ")
        sentence = " ".join(
            sentence.split()
        )  # Replace multiple spaces with a single space
        self.sentence_text_edit.setPlainText(sentence)

    def save_sentence(self) -> None:
        """
        Saves the current sentence, emits it as a signal, and clears the text editor.

        Emits:
            sentence_added_signal (str): The current sentence in the text editor.
        """
        sentence = self.sentence_text_edit.toPlainText()
        self.sentence_text_edit.clear()
        self.sentence_added_signal.emit(sentence)
        # TODO: Automatic new line removal if have it checked.


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = SentenceBin()
    ui.show()
    sys.exit(app.exec_())
