import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QToolBar,
    QAction,
    QMenu,
)
from PyQt5.QtGui import QIcon, QFont, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt, QSize


class BoldTextEdit(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Text Editor")
        self.setGeometry(100, 100, 600, 400)

        # Create the text edit widget
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)

        ### Format Toolbar
        self.format_tb = QToolBar(self)
        self.format_tb.setIconSize(QSize(16, 16))
        self.format_tb.setWindowTitle("Format Toolbar")

        self.actionTextBold = QAction(
            QIcon.fromTheme("format-text-bold-symbolic"),
            "&Bold",
            self,
            priority=QAction.LowPriority,
            shortcut=Qt.CTRL + Qt.Key_B,
            triggered=self.textBold,
            checkable=True,
        )
        self.actionTextBold.setStatusTip("bold")
        bold = QFont()
        bold.setBold(True)
        self.actionTextBold.setFont(bold)
        self.format_tb.addAction(self.actionTextBold)

        # Create menu bar
        self.formatMenu = QMenu("F&ormat", self)
        self.formatMenu.addAction(self.actionTextBold)

        self.show()

    def textBold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(
            self.actionTextBold.isChecked() and QFont.Bold or QFont.Normal
        )
        self.mergeFormatOnWordOrSelection(fmt)

    def mergeFormatOnWordOrSelection(self, format):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        self.text_edit.mergeCurrentCharFormat(format)

        #######

    #     # Create a bold action
    #     bold_action = QAction("Bold", self)
    #     bold_action.setShortcut("Ctrl+B")
    #     bold_action.triggered.connect(self.bold_text)

    #     # Add the bold action to the menu bar
    #     edit_menu = self.menuBar().addMenu("Edit")
    #     edit_menu.addAction(bold_action)

    #     self.is_bold = False  # Initialize bold state

    # def bold_text(self):
    #     cursor = self.text_edit.textCursor()
    #     selected_text = cursor.selectedText()

    #     # Check if there is selected text
    #     if selected_text:
    #         # Check if the selected text is already bold
    #         format = cursor.charFormat()
    #         font = format.font()
    #         if font.bold():
    #             font.setBold(False)
    #         else:
    #             font.setBold(True)

    #         # Apply the new format to the selected text
    #         format.setFont(font)
    #         cursor.mergeCharFormat(format)

    #     # Toggle bold state for future text
    #     self.is_bold = not self.is_bold
    #     print(f"is_bold = {self.is_bold}")

    # def keyPressEvent(self, event):
    #     # if event.key() == Qt.Key_B and event.modifiers() == Qt.ControlModifier:
    #     #     # If Ctrl+B is pressed, toggle bold state
    #     #     self.bold_text()
    #     #     event.accept()
    #     # else:
    #     # Otherwise, check if we should apply bold formatting
    #     if self.is_bold:
    #         cursor = self.text_edit.textCursor()
    #         format = cursor.charFormat()
    #         font = format.font()
    #         font.setBold(True)
    #         format.setFont(font)
    #         # cursor.mergeCharFormat(format)
    #         cursor.insertText(event.text(), format)

    #     super().keyPressEvent(event)

    def get_formatted_text(self):
        return self.text_edit.toHtml()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BoldTextEdit()
    sys.exit(app.exec_())


# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction
# from PyQt5.QtCore import Qt


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle("Text Editor")
#         self.setGeometry(100, 100, 600, 400)

#         # Create the text edit widget
#         self.text_edit = QTextEdit(self)
#         self.setCentralWidget(self.text_edit)

#         # Create a bold action
#         bold_action = QAction("Bold", self)
#         bold_action.setShortcut("Ctrl+B")
#         bold_action.triggered.connect(self.bold_text)

#         # Add the bold action to the menu bar
#         edit_menu = self.menuBar().addMenu("Edit")
#         edit_menu.addAction(bold_action)

#         self.is_bold = False  # Initialize bold state
#         self.show()

#     def bold_text(self):
#         cursor = self.text_edit.textCursor()
#         selected_text = cursor.selectedText()

#         # Check if there is selected text
#         if selected_text:
#             # Check if the selected text is already bold
#             format = cursor.charFormat()
#             font = format.font()
#             if font.bold():
#                 font.setBold(False)
#             else:
#                 font.setBold(True)

#             # Apply the new format to the selected text
#             format.setFont(font)
#             cursor.mergeCharFormat(format)

#         # Toggle bold state for future text
#         self.is_bold = not self.is_bold
#         print(f"is_bold = {self.is_bold}")

#     def keyPressEvent(self, event):
#         # if event.key() == Qt.Key_B and event.modifiers() == Qt.ControlModifier:
#         #     # If Ctrl+B is pressed, toggle bold state
#         #     self.bold_text()
#         #     event.accept()
#         # else:
#         # Otherwise, check if we should apply bold formatting
#         if self.is_bold:
#             cursor = self.text_edit.textCursor()
#             format = cursor.charFormat()
#             font = format.font()
#             font.setBold(True)
#             format.setFont(font)
#             # cursor.mergeCharFormat(format)
#             cursor.insertText(event.text(), format)

#         super().keyPressEvent(event)

#     def get_formatted_text(self):
#         return self.text_edit.toHtml()


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     sys.exit(app.exec_())


# # import sys
# # from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction

# # class MainWindow(QMainWindow):
# #     def __init__(self):
# #         super().__init__()

# #         self.initUI()

# #     def initUI(self):
# #         self.setWindowTitle("Text Editor")
# #         self.setGeometry(100, 100, 600, 400)

# #         # Create the text edit widget
# #         self.text_edit = QTextEdit(self)
# #         self.setCentralWidget(self.text_edit)

# #         # Create a bold action
# #         bold_action = QAction("Bold", self)
# #         bold_action.setShortcut("Ctrl+B")
# #         bold_action.triggered.connect(self.bold_text)

# #         # Add the bold action to the menu bar
# #         edit_menu = self.menuBar().addMenu("Edit")
# #         edit_menu.addAction(bold_action)

# #         self.show()

# #     def bold_text(self):
# #         cursor = self.text_edit.textCursor()
# #         selected_text = cursor.selectedText()

# #         if not selected_text:
# #             return

# #         # Check if the selected text is already bold
# #         format = cursor.charFormat()
# #         font = format.font()
# #         if font.bold():
# #             font.setBold(False)
# #         else:
# #             font.setBold(True)

# #         # Apply the new format to the selected text
# #         format.setFont(font)
# #         cursor.mergeCharFormat(format)

# #     def get_formatted_text(self):
# #         return self.text_edit.toHtml()


# # if __name__ == "__main__":
# #     app = QApplication(sys.argv)
# #     window = MainWindow()
# #     sys.exit(app.exec_())


# ######################################
# # old
# ######################################
# # import sys
# # from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit
# # from PyQt5.QtGui import QTextCursor, QTextCharFormat, QKeySequence, QFont


# # class TextEditor(QWidget):
# #     def __init__(self):
# #         super().__init__()
# #         self.initUI()

# #     def initUI(self):
# #         self.textEdit = QTextEdit(self)
# #         self.textEdit.setGeometry(50, 50, 300, 200)
# #         self.textEdit.textChanged.connect(self.onTextChanged)
# #         self.textEdit.setAcceptRichText(True)

# #         self.shortcut = QKeySequence("Ctrl+B")
# #         self.boldFormat = QTextCharFormat()
# #         self.boldFormat.setFontWeight(QFont.Bold)

# #         self.show()

# #     def onTextChanged(self):
# #         cursor = self.textEdit.textCursor()
# #         selected_text = cursor.selectedText()
# #         if selected_text:
# #             current_format = cursor.charFormat()
# #             if current_format.fontWeight() == QFont.Bold:
# #                 cursor.mergeCharFormat(self.boldFormat)
# #             else:
# #                 bold_char_format = QTextCharFormat()
# #                 bold_char_format.setFontWeight(QFont.Bold)
# #                 cursor.mergeCharFormat(bold_char_format)

# #     def keyPressEvent(self, event):
# #         if event.matches(self.shortcut):
# #             self.onShortcut()

# #     def onShortcut(self):
# #         cursor = self.textEdit.textCursor()
# #         selected_text = cursor.selectedText()
# #         if selected_text:
# #             current_format = cursor.charFormat()
# #             if current_format.fontWeight() == QFont.Bold:
# #                 cursor.mergeCharFormat(self.boldFormat)
# #             else:
# #                 bold_char_format = QTextCharFormat()
# #                 bold_char_format.setFontWeight(QFont.Bold)
# #                 cursor.mergeCharFormat(bold_char_format)

# #     def getFormattedText(self):
# #         return self.textEdit.toHtml()


# # if __name__ == "__main__":
# #     app = QApplication(sys.argv)
# #     ex = TextEditor()
# #     sys.exit(app.exec_())
