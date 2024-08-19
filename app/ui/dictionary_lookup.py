import sys
from typing import List, Dict

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
)


# Stylesheet for the button for each dictionary
BUTTON_STYLE = """
QPushButton {
    background-color: #f2f2f2;
    color: #333333;
    border: none;
    padding: 8px 16px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #e6e6e6;
}
QPushButton:pressed {
    background-color: #d9d9d9;
}
"""


class DictionaryLookup(QWidget):
    """
    A widget that allows users to look up words in dictionaries in various languages.

    Signals:
        search_requested (pyqtSignal): Signal emitted when a search is requested, passing the language and dictionary name.
    """

    search_requested = pyqtSignal(str, str)

    def __init__(self) -> None:
        """Initialises the DictionaryLookup widget and its UI components."""
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """Sets up the user interface for the DictionaryLookup widget."""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.dictionary_lookup_label = QLabel("Dictionary Lookup:")
        self.dictionary_lookup_lineedit = QLineEdit()
        self.search_button = QPushButton("Search")

        self.dictionary_lookup_layout = QHBoxLayout()
        self.dictionary_lookup_layout.addWidget(self.dictionary_lookup_label)
        self.dictionary_lookup_layout.addWidget(self.dictionary_lookup_lineedit)
        self.dictionary_lookup_layout.addWidget(self.search_button)

        # Create a tab for each language's dictionaries
        self.tab_widget = QTabWidget()

        self.layout.addLayout(self.dictionary_lookup_layout)
        self.layout.addWidget(self.tab_widget)

    def set_up_dictionaries(self, dictionaries: Dict[str, List[str]]) -> None:
        """
        Sets up tabs for each language with entries for each available dictionary.

        Args:
            dictionaries (dict[str, list[str]]): A dictionary where keys are language names and values are lists of dictionaries for each language.
        """

        # TODO: allow updating dictionaries while the program is running, e.g. with self.clear_dictionaries()

        for language, dictionaries in dictionaries.items():
            if language == "English" or dictionaries == []:
                # TODO: Allow for English dictionaries (English monolingual, and English to target language dictionaries)
                continue

            # Create a QWidget for the tab
            tab = QWidget()

            # Create a QVBoxLayout to hold the checkboxes and buttons
            dictionaries_layout = QVBoxLayout()
            dictionaries_layout.setSpacing(1)
            dictionaries_layout.setContentsMargins(0, 0, 0, 0)  # Set to zero margin

            # Set the QVBoxLayout as the layout for the tab
            tab.setLayout(dictionaries_layout)

            for dictionary in dictionaries:
                container_widget = QWidget()
                container_widget.setObjectName("container_widget")

                container_layout = QHBoxLayout(container_widget)
                container_layout.setSpacing(5)
                container_layout.setContentsMargins(2, 2, 2, 2)

                checkbox = QCheckBox()
                checkbox.setFixedSize(20, 20)
                checkbox.setChecked(
                    True
                )  # TODO: Check true if given dictionary has been favourited by a user!
                container_layout.addWidget(checkbox)

                button = QPushButton(dictionary)
                button.setStyleSheet(BUTTON_STYLE)
                # button.setProperty("class", "flat")  # Set the 'flat' style
                button.clicked.connect(
                    lambda _, lang=language, dict_name=dictionary: self.search_requested.emit(
                        lang, dict_name
                    )
                )

                container_layout.addWidget(button)
                dictionaries_layout.addWidget(container_widget)

            self.tab_widget.addTab(tab, language)

    def get_text(self) -> str:
        """
        Retrieves the text entered in the dictionary lookup line edit.

        Returns:
            str: The word or phrase entered by the user.
        """
        word = self.dictionary_lookup_lineedit.text()
        word = word.replace("­", "")  # Removing soft hyphens
        return word

    def get_language(self) -> str:
        """
        Retrieves the currently selected language from the tab widget.

        Returns:
            str: The name of the currently selected language.
        """
        # Get the index of the currently selected tab
        current_tab_index = self.tab_widget.currentIndex()

        # Get the name of the tab corresponding to the currently selected tab index
        language = self.tab_widget.tabText(current_tab_index)
        return language

    def get_selected_dictionaries(self, language: str) -> List[str]:
        """
        Retrieve the names of selected dictionaries for a specified language tab.

        Args:
            language (str): The language associated with the tab to retrieve dictionaries from.

        Returns:
            List[str]: A list of selected dictionary names.
        """
        dictionaries = []

        # Find the tab with the given language
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == language:
                tab = self.tab_widget.widget(i)
                break
        else:
            return dictionaries

        ## If only interested in the current tab:
        # tab = self.tab_widget.currentWidget()

        # Get the names of the dictionaries with checked checkboxes
        for widget in tab.findChildren(QWidget):
            if (
                widget.objectName() == "container_widget"
                and widget.findChild(QCheckBox).isChecked()
            ):
                dictionary_name = widget.findChild(QPushButton).text()
                dictionaries.append(dictionary_name)

        return dictionaries

    def clear_dictionaries(self):
        """Clears all tabs and dictionaries from the tab widget."""
        self.tab_widget.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = DictionaryLookup()
    dictionaries = {
        "Spanish": [
            "Larousse Dictionary",
            "Oxford Dictionary",
            "Spanish Dict",
            "Collins",
            "Reverso",
        ],
        "French": ["Larousse Dictionary"],
    }
    widget.set_up_dictionaries(dictionaries)
    widget.search_button.clicked.connect(
        lambda: print(widget.get_selected_dictionaries("Spanish"))
    )
    widget.show()
    sys.exit(app.exec_())
