import sys
from PyQt5.QtWidgets import QApplication
from src.ui import PuzzleWindow

def main():
    """Entry point của ứng dụng"""
    app = QApplication(sys.argv)
    window = PuzzleWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 