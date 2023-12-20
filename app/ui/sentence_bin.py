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
import sys


class SentenceBin(QMainWindow):
    sentence_added_signal = pyqtSignal(str)
    # close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
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

        self.remove_new_lines_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.remove_new_lines_shortcut.activated.connect(self.remove_new_lines)

        # Create a button to save the sentence
        self.save_button = QPushButton("Save Sentence (Ctrl+Enter)", self)
        self.save_button.clicked.connect(self.save_sentence)
        self.layout.addWidget(self.save_button)

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.save_shortcut.activated.connect(self.save_sentence)

        # Close the sentence bin when ESC is pressed and the widget is in focus
        self.close_action = QAction(
            self
        )  # QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.close_action.setShortcut(QKeySequence(Qt.Key_Escape))

        self.close_action.triggered.connect(self.close)

        # Add the QAction to the window
        self.addAction(self.close_action)

    def remove_new_lines(self):
        ##!! change "sentence" to "text"
        sentence = self.sentence_text_edit.toPlainText()
        sentence = sentence.replace("\n", " ")
        sentence = " ".join(sentence.split())  # quick way of replacing multiple spaces
        self.sentence_text_edit.setPlainText(sentence)

    ##!!?? this needs to be created in controller, as str emitted needs to be added to model?
    def save_sentence(self):
        # Implement the save_sentence function here
        sentence = self.sentence_text_edit.toPlainText()
        self.sentence_text_edit.clear()
        self.sentence_added_signal.emit(sentence)
        ##!! add automatic new line removal if have it checked!!


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = SentenceBin()
    ui.show()
    sys.exit(app.exec_())
