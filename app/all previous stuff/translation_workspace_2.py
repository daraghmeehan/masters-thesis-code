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

from PyQt5 import QtCore


class TranslationWorkspace(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set up the layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        ##!! make this separate function??
        # Language selection at the very top
        self.language_selection_layout = QHBoxLayout()

        self.target_language_label = QLabel("Target Language: ")
        self.target_language_dropdown = QComboBox()
        self.swap_button = QPushButton("<->")
        self.source_language_label = QLabel("Source Language: ")
        self.source_language_dropdown = QComboBox()

        self.language_selection_layout.addWidget(self.target_language_label)
        self.language_selection_layout.addWidget(self.target_language_dropdown)
        self.language_selection_layout.addWidget(self.swap_button)
        self.language_selection_layout.addWidget(self.source_language_label)
        self.language_selection_layout.addWidget(self.source_language_dropdown)

        self.layout.addLayout(self.language_selection_layout)

        # Target language section next
        self.target_language_layout = QHBoxLayout()

        self.target_language_textedit = QPlainTextEdit()
        self.translate_button = QPushButton("Translate")
        self.target_language_layout.addWidget(self.target_language_textedit)
        self.target_language_layout.addWidget(self.translate_button)

        self.layout.addLayout(self.target_language_layout)

        # Main translation section
        self.main_translation_layout = QHBoxLayout()

        # self.main_translation_layout.setContentsMargins(0, 0, 0, 0)
        # self.main_translation_layout.setSpacing(10)

        self.main_translation_textedit = QPlainTextEdit()
        self.main_translation_button = QPushButton("->")
        self.main_translation_layout.addWidget(self.main_translation_textedit)
        self.main_translation_layout.addWidget(self.main_translation_button)

        self.layout.addLayout(self.main_translation_layout)

        # Alternative translations section
        self.alt_translations_layout = QVBoxLayout()

        # Create scroll area widget
        self.alt_translations_scroll_area = QScrollArea()
        self.alt_translations_scroll_area.setWidgetResizable(True)  ##!! want this??
        # # self.alt_translations_scroll_area.setFrameShape(QScrollArea.NoFrame)
        # # self.alt_translations_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.alt_translations_scroll_widget = QWidget()
        self.alt_translations_scroll_area.setWidget(self.alt_translations_scroll_widget)

        # # Create VBox layout for scroll widget
        # self.alt_translations_layout = QVBoxLayout(self.alt_translations_scroll_widget)
        # self.alt_translations_layout.setAlignment(QtCore.Qt.AlignTop)  ##!! need this??

        # for i in range(4):
        #     alt_translations_x_layout = QHBoxLayout()
        #     alt_translations_text_edit = QPlainTextEdit()
        #     alt_translations_button = QPushButton("->")

        #     alt_translations_x_layout.addWidget(alt_translations_text_edit)
        #     alt_translations_x_layout.addWidget(alt_translations_button)

        #     self.alt_translations_layout.addLayout(alt_translations_x_layout)

        # self.alt_translations_scroll_area.setWidget(self.alt_translations_scroll_widget)
        self.alt_translations_layout.addWidget(self.alt_translations_scroll_area)

        self.layout.addLayout(self.alt_translations_layout)
