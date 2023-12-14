import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
)


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        # grid.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # # First object in the right 1/4 of the screen
        label1 = QPlainTextEdit("Object 1")
        # # grid.addWidget(label1, 0, 3, 4, 1)

        # # Second object in the top right corner
        label2 = QPlainTextEdit("Object 2")
        # # grid.addWidget(label2, 0, 0, 3, 3)

        # # Third and fourth objects in the bottom 1/4 on the left
        label3 = QPlainTextEdit("Object 3")
        # # grid.addWidget(label3, 4, 0, 1, 1)
        label4 = QPlainTextEdit("Object 4")
        # # grid.addWidget(label4, 4, 2, 1, 1)

        grid.addWidget(label1, 0, 0, 3, 3)
        grid.addWidget(label2, 0, 3, 4, 1)
        grid.addWidget(label3, 3, 0, 1, 2)
        grid.addWidget(label4, 3, 2, 1, 1)
        # grid.addWidget(label1, 0, 0, 2, 2)
        # grid.addWidget(label2, 0, 2, 3, 1)
        # grid.addWidget(label3, 2, 0)
        # grid.addWidget(label4, 2, 1)
        for i in range(0, 4):
            grid.setColumnStretch(i, 1)
            grid.setRowStretch(i, 1)
        # grid.setColumnStretch(0, 1)
        # grid.setColumnStretch(1, 1)
        # grid.setRowStretch(0, 1)
        # grid.setRowStretch(1, 1)

        print(grid.rowCount())
        print(grid.columnCount())

        # for i in range(1, 5):
        #     for j in range(1, 5):
        #         if i == 4 and j == 2:
        #             grid.addWidget(QPlainTextEdit("special"), i, j, 1, 3)
        #         elif i == 4 and (j == 4 or j == 3):
        #             continue
        #         else:
        #             grid.addWidget(QPlainTextEdit("B" + str(i) + str(j)), i, j)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("PyQt Grid Layout Example")
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
