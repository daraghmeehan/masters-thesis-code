from typing import List

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QLabel,
    QComboBox,
)


class TranslationWorkspace(QWidget):
    """A PyQt5 widget for translating text between two languages."""

    def __init__(self) -> None:
        """Initialise the translation workspace widget and its components."""
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """Initialise the user interface components."""
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Source Language Section
        self.setup_source_language_section()

        # Swap Button
        self.swap_languages_button = QPushButton("<->", clicked=self.swap_langauges)
        self.swap_languages_button.setFixedWidth(40)

        # Target Language Section
        self.setup_target_language_section()

        # Action Buttons
        self.setup_action_buttons()

        # Add components to the main layout
        self.layout.addLayout(self.source_language_layout)
        self.layout.addWidget(self.swap_languages_button)
        self.layout.addLayout(self.target_language_layout)
        self.layout.addLayout(self.button_layout)

    def setup_source_language_section(self) -> None:
        """Set up the UI components for the source language selection and text input."""
        self.source_language_label = QLabel("Source Language:")
        self.source_language_dropdown = QComboBox()
        self.source_language_textedit = QPlainTextEdit()

        self.source_language_choice_layout = QHBoxLayout()
        self.source_language_choice_layout.addWidget(self.source_language_label, 1)
        self.source_language_choice_layout.addWidget(self.source_language_dropdown, 3)

        self.source_language_layout = QVBoxLayout()
        self.source_language_layout.addLayout(self.source_language_choice_layout)
        self.source_language_layout.addWidget(self.source_language_textedit)

    def setup_target_language_section(self) -> None:
        """Set up the UI components for the target language selection."""
        self.target_language_label = QLabel("Target Language:")
        self.target_language_dropdown = QComboBox()
        self.target_language_textedit = QPlainTextEdit()

        self.target_language_choice_layout = QHBoxLayout()
        self.target_language_choice_layout.addWidget(self.target_language_label, 1)
        self.target_language_choice_layout.addWidget(self.target_language_dropdown, 3)

        self.target_language_layout = QVBoxLayout()
        self.target_language_layout.addLayout(self.target_language_choice_layout)
        self.target_language_layout.addWidget(self.target_language_textedit)

    def setup_action_buttons(self) -> None:
        """Set up the action buttons for translation and flashcard creation."""
        self.translate_button = QPushButton(
            "Translate"
        )  # TODO: Add shortcut "\n(Alt+T)"
        self.flashcard_button = QPushButton("-> F")  # TODO: Add shortcut \n(Alt+F)")

        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.translate_button)
        self.button_layout.addWidget(self.flashcard_button)

    def set_languages(
        self, languages: List[str], source_language: str, target_language: str
    ) -> None:
        """
        Populate the language dropdowns with available languages and set the initial selections.

        Args:
            languages (List[str]): List of language names to populate the dropdowns.
            source_language (str): The initial source language to be selected.
            target_language (str): The initial target language to be selected.
        """
        self.source_language_dropdown.addItems(languages)
        self.target_language_dropdown.addItems(languages)

        self.set_source_language(source_language)
        self.set_target_language(target_language)

    def swap_langauges(self) -> None:
        """Swap the selected source and target languages and their corresponding text."""
        source_language = self.get_source_language()
        target_language = self.get_target_language()
        self.set_source_language(target_language)
        self.set_target_language(source_language)

        source_language_text = self.get_source_language_text()
        target_language_text = self.get_target_language_text()
        self.set_source_language_text(target_language_text)
        self.set_target_language_text(source_language_text)

    def get_source_language(self) -> str:
        return self.source_language_dropdown.currentText()

    def get_target_language(self) -> str:
        return self.target_language_dropdown.currentText()

    def set_source_language(self, language: str) -> None:
        self.source_language_dropdown.setCurrentText(language)

    def set_target_language(self, language: str) -> None:
        self.target_language_dropdown.setCurrentText(language)

    def get_source_language_text(self) -> str:
        return self.source_language_textedit.toPlainText()

    def get_target_language_text(self) -> str:
        return self.target_language_textedit.toPlainText()

    def set_source_language_text(self, text: str) -> None:
        self.source_language_textedit.setPlainText(text)

    def set_target_language_text(self, text: str) -> None:
        self.target_language_textedit.setPlainText(text)

    def clear_workspace(self) -> None:
        """Clear the text in both the source and target language text edit widgets."""
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
