from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QShortcut,
    QCheckBox,
    QLabel,
    QSizePolicy,
    QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence, QFont, QFontMetrics, QTextOption


class StudyMaterials(QWidget):
    def __init__(self, mode, languages):
        super().__init__()

        # Create a tab for each type of study material
        self.tab_widget = QTabWidget()

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)

        # TODO def add_tab(self, mode): # future allow making new tabs
        if mode == "Text":
            self.saved_sentences_tab = QWidget()
            saved_sentences_layout = QVBoxLayout()
            self.saved_sentences = SavedSentences()
            saved_sentences_layout.addWidget(self.saved_sentences)
            self.saved_sentences_tab.setLayout(saved_sentences_layout)
            self.tab_widget.addTab(self.saved_sentences_tab, "Saved Sentences")

        elif mode == "AVI":
            self.subtitle_workspace_tab = QWidget()
            subtitle_workspace_layout = QVBoxLayout()
            self.subtitle_workspace = SubtitleWorkspace(languages)
            subtitle_workspace_layout.addWidget(self.subtitle_workspace)
            self.subtitle_workspace_tab.setLayout(subtitle_workspace_layout)
            self.tab_widget.addTab(self.subtitle_workspace_tab, "Subtitle Workspace")

        self.setLayout(main_layout)


# class SubtitleWorkspace(QWidget):
#     def __init__(self):
#         super().__init__()

#         # Create 3 text edits
#         self.textedit_1 = QPlainTextEdit(self)
#         self.textedit_2 = QPlainTextEdit(self)
#         self.textedit_3 = QPlainTextEdit(self)

#         # Create a vertical layout and add the line edits to it
#         layout = QHBoxLayout(self)
#         layout.addWidget(self.textedit_1)
#         layout.addWidget(self.textedit_2)
#         layout.addWidget(self.textedit_3)

#     def update_subtitle_view(self, subtitle_text):
#         self.textedit_1.setPlainText(subtitle_text)


class SegmentHeader(QWidget):
    listen_requested_signal = pyqtSignal(datetime, datetime, str)  # Define the signal

    def __init__(
        self,
        segment_number,
        total_segments,
        languages_with_subtitles,
        languages_with_audio_track,
    ):
        super().__init__()
        self.segment_number = segment_number

        self.layout = QVBoxLayout()

        # First horizontal box for segment_number/total_segments and timings
        self.header_info_layout = QHBoxLayout()
        self.layout.addLayout(self.header_info_layout)

        # Left label for segment info
        segment_label = QLabel(f"Segment {segment_number}/{total_segments}:")
        self.header_info_layout.addWidget(segment_label, 1, alignment=Qt.AlignRight)

        # Right label for time range
        self.time_label = QLabel(" -> ")
        self.header_info_layout.addWidget(self.time_label, 1, alignment=Qt.AlignLeft)

        self.languages_layout = QHBoxLayout()
        self.layout.addLayout(self.languages_layout)

        # Second horizontal box for languages
        for language in languages_with_subtitles:
            has_audio_track = language in languages_with_audio_track
            language_layout = self.create_language_layout(language, has_audio_track)
            self.languages_layout.addLayout(language_layout)

        self.setLayout(self.layout)  # Set the main layout of the widget

    def add_timings(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

        start_time_str = start_time.strftime("%H:%M:%S")
        end_time_str = end_time.strftime("%H:%M:%S")
        self.time_label.setText(f"{start_time_str} -> {end_time_str}")

    def create_language_layout(self, language, has_audio_track):
        language_layout = QHBoxLayout()  # Create a QHBoxLayout for each language column

        # Add empty space
        language_layout.addStretch(1)

        # Add language name label
        language_name_label = QLabel(language)
        label_alignment = Qt.AlignRight if has_audio_track else Qt.AlignCenter
        language_layout.addWidget(language_name_label, 1, alignment=label_alignment)

        if has_audio_track:
            # Add listen button
            listen_button = QPushButton("🔊")
            listen_button.setFixedSize(20, 20)
            listen_button.clicked.connect(
                lambda _, lang=language: self.emit_listen_request(lang)
            )
            language_layout.addWidget(listen_button, 1, alignment=Qt.AlignLeft)

        # Add empty space
        language_layout.addStretch(1)

        return language_layout

    def emit_listen_request(self, language):
        self.listen_requested_signal.emit(self.start_time, self.end_time, language)


class SubtitleView(QWidget):
    listen_requested_signal = pyqtSignal()
    flashcard_requested_signal = pyqtSignal()

    def __init__(self, text, has_audio_track):
        super().__init__()
        self.initUI(text, has_audio_track)

    def initUI(self, text, has_audio_track):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add a checkbox to the left of the subtitle
        checkbox = QCheckBox()
        layout.addWidget(checkbox, alignment=Qt.AlignTop)

        self.subtitle_view = QPlainTextEdit(text)
        self.subtitle_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )  # Turn off vertical scroll bar
        self.subtitle_view.setReadOnly(True)

        layout.addWidget(self.subtitle_view)

        # Vertical layout for buttons
        buttons_layout = QVBoxLayout()

        if has_audio_track:
            listen_button = QPushButton("🔊")
            listen_button.setFixedSize(20, 20)
            listen_button.clicked.connect(self.listen_requested_signal.emit)
            buttons_layout.addWidget(listen_button)

        flashcard_button = QPushButton("F")
        flashcard_button.setFixedSize(20, 20)
        flashcard_button.clicked.connect(self.flashcard_requested_signal.emit)
        buttons_layout.addWidget(flashcard_button)

        # Add buttons_layout to the main horizontal layout
        layout.addLayout(buttons_layout)


class SubtitleWorkspace(QWidget):
    flashcard_requested_signal = pyqtSignal(str, int)  # Language, subtitle index
    listen_requested_signal = pyqtSignal(str, int)  # Language, subtitle index

    def __init__(self, languages):
        super().__init__()

        self.languages = languages
        self.languages_with_subtitles = []
        self.languages_with_audio_tracks = []

        self.entry_layouts = []  # List to store layouts for each entry
        self.main_layout = QHBoxLayout(self)  # Main layout to hold language layouts
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Create a container widget for the layout and set it to the scroll area
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        self.scroll_area.setWidget(self.container_widget)

        # Add the scroll area to the main layout
        self.main_layout.addWidget(self.scroll_area)

    def clear_workspace(self):
        pass

    def add_segment_header(self, current_segment, num_segments):
        # if current_segment != 1:
        #     # If not at first segment, add a separator line when adding a new segment
        #     separating_line = create_separator_line()
        #     self.container_layout.addWidget(separating_line)
        segment_header = SegmentHeader(
            segment_number=current_segment,
            total_segments=num_segments,
            languages_with_subtitles=self.languages_with_subtitles,
            languages_with_audio_track=self.languages_with_audio_tracks,
        )
        self.container_layout.addWidget(segment_header)
        return segment_header

    def add_entry(self, entry):
        entry_layout = QHBoxLayout()  # Create a QHBoxLayout for the entry
        entry_layout.setContentsMargins(0, 0, 0, 0)
        entry_layout.setSpacing(5)

        self.container_layout.addLayout(
            entry_layout
        )  # Add entry layout to container layout
        self.entry_layouts.append(entry_layout)

        subtitle_views = []  # List to store subtitle views

        for language in self.languages_with_subtitles:
            has_audio_track = language in self.languages_with_audio_tracks

            subtitle_layout = QVBoxLayout()  # Create a QVBoxLayout for each language
            subtitle_layout.setContentsMargins(0, 0, 0, 0)
            subtitle_layout.setSpacing(0)
            entry_layout.addLayout(
                subtitle_layout
            )  # Add language layout to entry layout

            subtitle_indices, subtitle_texts = (
                entry[language]["indices"],
                entry[language]["texts"],
            )

            if subtitle_indices == []:
                subtitle_view = SubtitleView("", has_audio_track=False)
                subtitle_layout.addWidget(subtitle_view)
                subtitle_views.append(subtitle_view)
            else:
                for subtitle_index, subtitle_text in zip(
                    subtitle_indices, subtitle_texts
                ):
                    subtitle_view = SubtitleView(subtitle_text, has_audio_track)

                    subtitle_view.listen_requested_signal.connect(
                        lambda language=language, index=subtitle_index: self.listen_requested_signal.emit(
                            language, index
                        )
                    )
                    subtitle_view.flashcard_requested_signal.connect(
                        lambda language=language, index=subtitle_index: self.flashcard_requested_signal.emit(
                            language, index
                        )
                    )
                    subtitle_layout.addWidget(
                        subtitle_view
                    )  # Add subtitle view to the entry layout
                    subtitle_views.append(subtitle_view)

        ## In future, need to resize the subtitle views at the end of setting up the UI when they have been shrunk (then can calculate widget width accurately)
        # Calculate the minimum height required based on the maximum content
        max_height = 0
        for subtitle_view in subtitle_views:
            text = subtitle_view.subtitle_view.toPlainText()
            font_metrics = QFontMetrics(subtitle_view.subtitle_view.font())
            text_width = font_metrics.horizontalAdvance(text)

            # Ensure the widget width is accurate at the time of calculation
            subtitle_view.subtitle_view.adjustSize()
            # Estimate the number of lines by dividing the text width by the widget's width
            # widget_width = subtitle_view.subtitle_view.width()
            # print(widget_width)
            if len(self.languages_with_subtitles) < 3:
                widget_width = 150
            elif 3 <= len(self.languages_with_subtitles) <= 6:
                widget_width = 80
            elif 6 < len(self.languages_with_subtitles):
                widget_width = 45
            estimated_lines = (text_width // widget_width) + (
                1 if text_width % widget_width else 0
            )

            line_height = font_metrics.height()
            estimated_text_height = line_height * estimated_lines

            # # max_height = max(max_height, document_height + content_margins)
            max_height = int(max(max_height, estimated_text_height))

        max_height += 22

        # Set the minimum height for all subtitle views
        for subtitle_view in subtitle_views:
            subtitle_view.subtitle_view.setMinimumHeight(max_height)

        ## ??
        # Create and add subtitle views

    #     for index, subtitle in enumerate(subtitles):
    #         subtitle_view = self.create_subtitle_view(subtitle.text, language, index)
    #         language_layout.addWidget(subtitle_view)
    #         self.subtitle_views[language].append(subtitle_view)

    # def create_subtitle_view(self, text, language, index):
    #     subtitle_view = SubtitleView(text)

    #     # Connect signals from the subtitle view to the workspace signals
    #     subtitle_view.listen_requested_signal.connect(
    #         lambda: self.listen_requested_signal.emit(language, index)
    #     )
    #     subtitle_view.flashcard_requested_signal.connect(
    #         lambda: self.flashcard_requested_signal.emit(language, index)
    #     )

    #     return subtitle_view

    # def on_flashcard_button_clicked(self, subtitle):
    #     # Handle flashcard creation for the subtitle
    #     pass  # Implement here


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
        self.add_new_cards_button = QPushButton("Add from Sentence Bin")  # \n(Alt+B)")
        # self.add_new_cards_button.clicked.connect(self.add_new_cards)
        self.add_new_from_clipboard_button = QPushButton(
            "Add from Clipboard"
        )  # \n(Alt+C)")
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
        self.remove_button = QPushButton("X")  # \n(Alt+X)")
        # self.remove_button.setFixedSize(25, 25)
        self.remove_button.setFixedSize(65, 20)
        self.remove_button.setStyleSheet(
            "background-color: rgb(255, 0, 0); color: white; border-radius: 1px; font-weight: bold;"
        )
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
        self.translate_button = QPushButton("Translate")  # \n(Alt+G)")
        # self.translate_button.clicked.connect(lambda: self.translate_entry(self))
        self.translate_button.setFixedWidth(65)
        self.translate_button.clicked.connect(
            lambda: self.translate_requested_signal.emit(self)
        )
        self.flashcard_button = QPushButton("Flashcard")  # \n(Alt+Z)")
        # self.flashcard_button.clicked.connect(lambda: self.show_flashcard(self))
        self.flashcard_button.setFixedWidth(65)
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


def create_separator_line():
    separator_line = QFrame()
    separator_line.setFrameShape(QFrame.HLine)
    separator_line.setFrameShadow(QFrame.Sunken)
    separator_line.setStyleSheet("background-color: gray; height: 2px;")

    separator_layout = QHBoxLayout()
    separator_layout.addWidget(separator_line)
    separator_layout.setContentsMargins(0, 6, 0, 0)
    separator_layout.setSpacing(0)

    separator_widget = QWidget()
    separator_widget.setLayout(separator_layout)

    return separator_widget
