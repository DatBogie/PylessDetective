import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QCheckBox, QComboBox, QLabel
from main import get_maps, get_clues, get_suspects

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PylessDetective GUI")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())