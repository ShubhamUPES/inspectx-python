from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from app.ui.theme import (TONE, GRAY_200, GRAY_400, GRAY_500, GRAY_700,
                           GRAY_900, WHITE, VIOLET_600)


class Card(QWidget):
    """A white rounded card with optional title, subtitle, and tone accent."""

    def __init__(self, title: str = "", subtitle: str = "",
                 tone: str = "gray", parent=None):
        super().__init__(parent)
        self._tone = tone
        t = TONE.get(tone, TONE["gray"])

        self.setObjectName("Card")
        self.setStyleSheet(f"""
            QWidget#Card {{
                background: {WHITE};
                border: 1px solid {GRAY_200};
                border-radius: 16px;
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(8)

        if title:
            hdr = QWidget()
            hdr.setStyleSheet("background:transparent;border:none;")
            hl = QVBoxLayout(hdr)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(2)
            t_lbl = QLabel(title)
            t_lbl.setStyleSheet(
                f"font-size:14px;font-weight:700;color:{GRAY_900};"
                f"background:transparent;border:none;"
            )
            hl.addWidget(t_lbl)
            if subtitle:
                s_lbl = QLabel(subtitle)
                s_lbl.setStyleSheet(
                    f"font-size:11px;color:{GRAY_500};"
                    f"background:transparent;border:none;"
                )
                hl.addWidget(s_lbl)
            outer.addWidget(hdr)

            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(f"color:{GRAY_200};border:none;background:{GRAY_200};max-height:1px;")
            outer.addWidget(sep)

        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)
        outer.addLayout(self._content_layout)

    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    def add_widget(self, widget):
        self._content_layout.addWidget(widget)

    def add_layout(self, layout):
        self._content_layout.addLayout(layout)
