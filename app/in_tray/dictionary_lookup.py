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
import sys

# from PyQt5 import QtCore

# if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
#     QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
# if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
#     QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class DictionaryLookup(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Set up the layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.dictionary_lookup_label = QLabel("Dictionary Lookup:")
        self.dictionary_lookup_lineedit = QLineEdit()
        self.search_button = QPushButton("Search")

        self.dictionary_lookup_layout = QHBoxLayout()
        self.dictionary_lookup_layout.addWidget(self.dictionary_lookup_label)
        self.dictionary_lookup_layout.addWidget(self.dictionary_lookup_lineedit)
        self.dictionary_lookup_layout.addWidget(self.search_button)

        # Create a tab for each languages' dictionaries
        self.tab_widget = QTabWidget()

        self.layout.addLayout(self.dictionary_lookup_layout)
        self.layout.addWidget(self.tab_widget)

    def set_up_dictionaries(self, dictionaries):
        # self.clear_dictionaries()

        button_style = """
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

        for language, dictionaries in dictionaries.items():
            if language == "English" or dictionaries == []:
                continue

            # Create a QWidget for the tab
            tab = QWidget()

            # Create a QVBoxLayout to hold the checkboxes and buttons
            dictionaries_layout = QVBoxLayout()
            dictionaries_layout.setSpacing(1)
            dictionaries_layout.setContentsMargins(0, 0, 0, 0)  # set to zero margin

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
                checkbox.setChecked(True)  ##??if in favourites??
                container_layout.addWidget(checkbox)

                button = QPushButton(dictionary)
                button.setStyleSheet(button_style)
                # button.setProperty("class", "flat")  # Set the 'flat' style
                # button.setStyleSheet("background-color: red;")
                container_layout.addWidget(button)

                # Add the QHBoxLayout to the QVBoxLayout
                dictionaries_layout.addWidget(container_widget)

            # Add the tab to the tab widget
            self.tab_widget.addTab(tab, language)

    def get_dictionaries(self, language):
        dictionaries = []

        # Find the tab with the given language
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == language:
                tab = self.tab_widget.widget(i)
                break
        else:
            return dictionaries

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
        lambda: print(widget.get_dictionaries("Spanish"))
    )
    widget.show()
    sys.exit(app.exec_())
