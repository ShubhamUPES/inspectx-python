from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from app.ui.theme import TONE, GRAY_50, GRAY_200, GRAY_600


class Badge(QLabel):
    def __init__(self, text: str, tone: str = "gray", parent=None):
        super().__init__(text, parent)
        t = TONE.get(tone, TONE["gray"])
        self.setStyleSheet(f"""
            QLabel {{
                background: {t['bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(22)
