from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from app.ui.theme import WHITE, VIOLET_700, VIOLET_200, VIOLET_500


class Toast(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet(f"""
            QWidget {{
                background: {WHITE};
                border: 1px solid {VIOLET_200};
                border-radius: 12px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(8)

        self._dot = QLabel()
        self._dot.setFixedSize(8, 8)
        self._dot.setStyleSheet(
            f"background:{VIOLET_500};border-radius:4px;border:none;"
        )

        self._label = QLabel()
        self._label.setStyleSheet(
            f"font-size:13px;font-weight:600;color:{VIOLET_700};"
            f"background:transparent;border:none;"
        )

        layout.addWidget(self._dot)
        layout.addWidget(self._label)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

        self.hide()

    def show_message(self, message: str, duration: int = 2000):
        self._label.setText(message)
        self.adjustSize()
        self._reposition()
        self.show()
        self._timer.start(duration)

    def _reposition(self):
        if self.parent():
            pw = self.parent().width()
            self.move(pw - self.width() - 20, 20)
