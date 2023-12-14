import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QTextEdit,
)


class ExampleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the main window properties
        self.setWindowTitle("Example Window")
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Create the layout for the left section of the window
        left_layout = QVBoxLayout()
        left_layout.addWidget(QTextEdit("Element 1 (3/4 of height)"), 3)
        left_layout.addWidget(QTextEdit("Element 2 (1/4 of height)"), 1)

        # Create the layout for the right section of the window
        right_layout = QVBoxLayout()
        right_layout.addWidget(QTextEdit("Element 3 (full height)"))

        # Add the left and right layouts to the main layout
        main_layout = QHBoxLayout(self.main_widget)
        main_layout.addLayout(left_layout, 3)  # Set stretch factor to 3 (3/4 of width)
        main_layout.addLayout(right_layout, 1)  # Set stretch factor to 1 (1/4 of width)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec_())
