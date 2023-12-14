from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QShortcut,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence


class StudyMaterials(QWidget):
    def __init__(self, mode):
        super().__init__()

        # Create a tab for each type of study material
        self.tab_widget = QTabWidget()

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)

        if mode == "AVI":
            self.subtitle_workspace_tab = QWidget()
            subtitle_workspace_layout = QVBoxLayout()
            self.subtitle_workspace = SubtitleWorkspace()
            subtitle_workspace_layout.addWidget(self.subtitle_workspace)
            self.subtitle_workspace_tab.setLayout(subtitle_workspace_layout)
            self.tab_widget.addTab(self.subtitle_workspace_tab, "Subtitle Workspace")

        self.saved_sentences_tab = QWidget()
        saved_sentences_layout = QVBoxLayout()
        self.saved_sentences = SavedSentences()
        saved_sentences_layout.addWidget(self.saved_sentences)
        self.saved_sentences_tab.setLayout(saved_sentences_layout)
        self.tab_widget.addTab(self.saved_sentences_tab, "Saved Sentences")

        self.setLayout(main_layout)


class SubtitleWorkspace(QWidget):
    def __init__(self):
        super().__init__()

        # Create 3 text edits
        self.textedit_1 = QPlainTextEdit(self)
        self.textedit_2 = QPlainTextEdit(self)
        self.textedit_3 = QPlainTextEdit(self)

        # Create a vertical layout and add the line edits to it
        layout = QHBoxLayout(self)
        layout.addWidget(self.textedit_1)
        layout.addWidget(self.textedit_2)
        layout.addWidget(self.textedit_3)

    def update_subtitle_view(self, subtitle_text):
        self.textedit_1.setPlainText(subtitle_text)


class SavedSentences(QWidget):
    translate_entry_signal = pyqtSignal(QWidget)
    make_flashcard_from_entry_signal = pyqtSignal(QWidget)

    def __init__(self):
        super().__init__()

        # Set up the layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # self.entries = []  ##!! continue here??
        # https://stackoverflow.com/questions/71261850/how-can-i-obtain-the-index-or-the-position-of-a-clicked-element-on-qgridlayout-p

        # Add the "Clear All" and "Translate All" buttons
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self.clear_all_entries)
        self.translate_all_button = QPushButton("Translate All")
        self.top_button_layout = QHBoxLayout()
        self.top_button_layout.addWidget(self.clear_all_button)
        self.top_button_layout.addWidget(self.translate_all_button)
        self.layout.addLayout(self.top_button_layout)

        ##!!should i be using listwidget??
        # Set up the scroll area for the entries
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFocusPolicy(Qt.NoFocus)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.layout.addWidget(self.scroll_area)

        # Set up the widget that contains the entries
        self.entries_widget = QWidget()
        self.entries_layout = QVBoxLayout()
        self.entries_layout.setSpacing(0)
        self.entries_layout.setContentsMargins(0, 0, 0, 0)
        self.entries_widget.setLayout(self.entries_layout)
        self.scroll_area.setWidget(self.entries_widget)
        # # Add some sample entries
        # for i in range(5):
        #     self.add_entry("Sentence " + str(i + 1))

        # Add the "Add New Cards" and "Add New from Clipboard" buttons
        self.add_new_cards_button = QPushButton("Add from Sentence Bin\n(Alt+B)")
        # self.add_new_cards_button.clicked.connect(self.add_new_cards)
        self.add_new_from_clipboard_button = QPushButton(
            "Add New from Clipboard\n(Alt+C)"
        )
        # self.add_new_from_clipboard_button.clicked.connect(self.add_new_from_clipboard)
        self.bottom_button_layout = QHBoxLayout()
        self.bottom_button_layout.addWidget(self.add_new_cards_button)
        self.bottom_button_layout.addWidget(self.add_new_from_clipboard_button)
        self.layout.addLayout(self.bottom_button_layout)

    def add_entry(self, text):
        text = text.replace("­", "")  # removing soft hyphens!
        entry = SavedSentenceEntry(text)
        self.entries_layout.addWidget(entry)

        entry.translate_requested_signal.connect(self.translate_entry_signal)
        entry.flashcard_requested_signal.connect(self.make_flashcard_from_entry_signal)

        # # Adjust the size of the widget containing the entries to update the scroll bar
        # self.entries_widget.adjustSize()

        # Move the scroll bar to the bottom
        ##!! this doesn't fully work!!
        scroll_bar = self.scroll_area.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    # def delete_focused_entry_widget(self):
    #     focused_widget = self.focusWidget()
    #     if focused_widget and isinstance(focused_widget.parent(), SavedSentenceEntry):
    #         focused_widget.parent().deleteLater()

    def get_all_saved_sentences(self):
        entry_indices = []
        sentences = []

        for i in range(self.entries_layout.count()):
            entry = self.entries_layout.itemAt(i).widget()
            sentence = entry.get_target_language_text()
            if sentence != "":
                entry_indices.append(i)
                sentences.append(sentence)

        return entry_indices, sentences

    def set_all_translations(self, entry_indices, translations):
        try:
            assert len(entry_indices) == len(translations)
        except:
            print("Entry indices and translations different :(")
            print(f"Entry indices: {entry_indices}")
            print(f"Translations: {translations}")
            return

        if entry_indices == []:
            return

        for entry_index, translations in zip(entry_indices, translations):
            entry = self.entries_layout.itemAt(entry_index).widget()
            entry.set_source_language_text(translations)

    def clear_all_entries(self):
        # Remove all entries from the layout
        # while self.entries_layout.count() > 0:
        #     self.entries_layout.itemAt(0).widget().deleteLater()
        # print(self.entries_layout.count())
        # self.entries_layout.itemAt(0).widget().deleteLater()
        # print(self.entries_layout.count())
        for i in reversed(range(self.entries_layout.count())):
            self.entries_layout.itemAt(i).widget().deleteLater()


class SavedSentenceEntry(QWidget):
    translate_requested_signal = pyqtSignal(QWidget)
    flashcard_requested_signal = pyqtSignal(QWidget)

    def __init__(self, text):
        super().__init__()

        self.entry_layout = QHBoxLayout()
        self.entry_layout.setSpacing(0)
        self.entry_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.entry_layout)

        # Add the "Remove Entry" button to the left of the entry
        self.remove_button = QPushButton("x\n(Alt+X)")
        # self.remove_button.setFixedSize(25, 25)
        self.remove_button.setFixedWidth(50)
        self.remove_button.clicked.connect(self.deleteLater)
        self.entry_layout.addWidget(self.remove_button)

        # Add the target language (saved text) to the left of the entry
        self.target_language_textedit = QPlainTextEdit()
        self.target_language_textedit.setPlainText(text)
        self.entry_layout.addWidget(self.target_language_textedit)

        # Add the translation to the right of the entry
        self.source_language_textedit = QPlainTextEdit()
        # self.source_language_textedit.setReadOnly(True)
        self.entry_layout.addWidget(self.source_language_textedit)

        # Add the "Translate" and "Flashcard" buttons to the right of the entry
        self.translate_button = QPushButton("Translate\n(Alt+G)")
        # self.translate_button.clicked.connect(lambda: self.translate_entry(self))
        self.translate_button.clicked.connect(
            lambda: self.translate_requested_signal.emit(self)
        )
        self.flashcard_button = QPushButton("Flashcard\n(Alt+Z)")
        # self.flashcard_button.clicked.connect(lambda: self.show_flashcard(self))
        self.flashcard_button.clicked.connect(
            lambda: self.flashcard_requested_signal.emit(self)
        )

        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.translate_button)
        self.button_layout.addWidget(self.flashcard_button)
        self.entry_layout.addLayout(self.button_layout)

        self.set_up_shortcuts()

    def get_target_language_text(self):
        return self.target_language_textedit.toPlainText()

    def get_source_language_text(self):
        return self.source_language_textedit.toPlainText()

    def set_target_language_text(self, text):
        self.target_language_textedit.setPlainText(text)

    def set_source_language_text(self, text):
        self.source_language_textedit.setPlainText(text)

    def set_up_shortcuts(self):
        self.remove_shortcut = QShortcut(QKeySequence("Alt+X"), self)
        self.remove_shortcut.activated.connect(self.remove_button.click)

        self.translate_shortcut = QShortcut(QKeySequence("Alt+G"), self)
        self.translate_shortcut.activated.connect(
            lambda: self.translate_requested_signal.emit(self)
        )
        # self.translate_button.click

        self.flashcard_shortcut = QShortcut(QKeySequence("Alt+Z"), self)
        self.flashcard_shortcut.activated.connect(
            lambda: self.flashcard_requested_signal.emit(self)
        )
        # self.flashcard_button.click
