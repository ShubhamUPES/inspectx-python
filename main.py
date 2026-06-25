"""
InspectX — Defect Detection Studio
Entry point: python main.py
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("InspectX")
    app.setOrganizationName("InspectX")

    # Global font
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()