from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QPushButton,
    QPlainTextEdit,
    QLabel,
    QComboBox,
)


class TranslationWorkspace(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set up the layout
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.source_language_label = QLabel("Source Language:")
        self.source_language_dropdown = QComboBox()
        self.source_language_textedit = QPlainTextEdit()

        self.source_language_choice_layout = QHBoxLayout()
        self.source_language_choice_layout.addWidget(self.source_language_label, 1)
        self.source_language_choice_layout.addWidget(self.source_language_dropdown, 3)

        self.source_language_layout = QVBoxLayout()
        self.source_language_layout.addLayout(self.source_language_choice_layout)
        self.source_language_layout.addWidget(self.source_language_textedit)

        self.swap_languages_button = QPushButton("<->", clicked=self.swap_langauges)
        self.swap_languages_button.setFixedWidth(40)

        self.target_language_label = QLabel("Target Language:")
        self.target_language_dropdown = QComboBox()
        self.target_language_textedit = QPlainTextEdit()

        self.target_language_choice_layout = QHBoxLayout()
        self.target_language_choice_layout.addWidget(self.target_language_label, 1)
        self.target_language_choice_layout.addWidget(self.target_language_dropdown, 3)

        self.target_language_layout = QVBoxLayout()
        self.target_language_layout.addLayout(self.target_language_choice_layout)
        self.target_language_layout.addWidget(self.target_language_textedit)

        self.translate_button = QPushButton("Translate")  # \n(Alt+T)")
        self.flashcard_button = QPushButton("-> F")  # \n(Alt+F)")

        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.translate_button)
        self.button_layout.addWidget(self.flashcard_button)

        self.layout.addLayout(self.source_language_layout)
        self.layout.addWidget(self.swap_languages_button)
        self.layout.addLayout(self.target_language_layout)
        self.layout.addLayout(self.button_layout)

    def set_languages(self, languages, source_language, target_language):
        self.source_language_dropdown.addItems(languages)
        self.target_language_dropdown.addItems(languages)

        self.set_source_language(source_language)
        self.set_target_language(target_language)

    def swap_langauges(self):
        source_language = self.get_source_language()
        target_language = self.get_target_language()
        self.set_source_language(target_language)
        self.set_target_language(source_language)

        source_language_text = self.get_source_language_text()
        target_language_text = self.get_target_language_text()
        self.set_source_language_text(target_language_text)
        self.set_target_language_text(source_language_text)

    def get_source_language(self):
        return self.source_language_dropdown.currentText()

    def get_target_language(self):
        return self.target_language_dropdown.currentText()

    def set_source_language(self, language):
        self.source_language_dropdown.setCurrentText(language)

    def set_target_language(self, language):
        self.target_language_dropdown.setCurrentText(language)

    def get_source_language_text(self):
        return self.source_language_textedit.toPlainText()

    def get_target_language_text(self):
        return self.target_language_textedit.toPlainText()

    def set_source_language_text(self, text):
        self.source_language_textedit.setPlainText(text)

    def set_target_language_text(self, text):
        self.target_language_textedit.setPlainText(text)

    def clear_workspace(self):
        self.source_language_textedit.setPlainText("")
        self.target_language_textedit.setPlainText("")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    languages = ["English", "Spanish", "French"]
    source_language = "Spanish"
    target_language = "English"

    app = QApplication(sys.argv)
    window = TranslationWorkspace()
    window.set_languages(languages, source_language, target_language)
    window.show()
    sys.exit(app.exec_())
