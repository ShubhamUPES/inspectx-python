from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.ui.theme import (TONE, GRAY_50, GRAY_200, GRAY_400, GRAY_500,
                           GRAY_700, GRAY_900, WHITE)


class MetricCard(QWidget):
    def __init__(self, label: str, value: str, tone: str = "gray", parent=None):
        super().__init__(parent)
        self._tone = tone
        self._build(label, value)

    def _build(self, label: str, value: str):
        t = TONE.get(self._tone, TONE["gray"])
        self.setStyleSheet(f"""
            QWidget {{
                background: {GRAY_50};
                border: 1px solid {GRAY_200};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size:10px;color:{GRAY_500};border:none;background:transparent;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)

        val = QLabel(str(value))
        val.setStyleSheet(
            f"font-size:14px;font-weight:700;color:{t['text']};border:none;background:transparent;"
        )
        val.setWordWrap(True)
        val.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(lbl)
        layout.addWidget(val)

    def update_value(self, label: str, value: str):
        while self.layout().count():
            item = self.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._build(label, value)
