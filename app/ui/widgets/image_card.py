from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QPainter
from pathlib import Path
from app.ui.theme import (
    WHITE, GRAY_50, GRAY_100, GRAY_200, GRAY_400, GRAY_700,
    GRAY_900, VIOLET_50, VIOLET_200, VIOLET_600,
    EMERALD_50, EMERALD_400,
)


def _placeholder_pixmap(w: int, h: int) -> QPixmap:
    px = QPixmap(w, h)
    px.fill(QColor("#1e293b"))
    painter = QPainter(px)
    painter.setPen(QColor("#475569"))
    painter.drawRect(0, 0, w - 1, h - 1)
    painter.drawLine(0, 0, w, h)
    painter.drawLine(w, 0, 0, h)
    painter.end()
    return px


class ImageCard(QWidget):
    clicked = pyqtSignal(int)   # emits image_id
    toggled = pyqtSignal(int, bool)  # emits image_id, selected

    def __init__(self, image_id: int, name: str, file_path: str,
                 status: str, compact: bool = False, parent=None):
        super().__init__(parent)
        self._image_id = image_id
        self._selected = False

        self.setObjectName("ImageCard")
        self._update_style(False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # Thumbnail
        thumb_h = 70 if compact else 100
        thumb = QLabel()
        thumb.setFixedHeight(thumb_h)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet("border-radius:8px;background:#1e293b;border:none;")
        if file_path and Path(file_path).exists():
            px = QPixmap(file_path).scaled(
                160, thumb_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            thumb.setPixmap(px)
        else:
            thumb.setPixmap(_placeholder_pixmap(160, thumb_h))
        root.addWidget(thumb)

        # Name row
        name_row = QHBoxLayout()
        name_row.setContentsMargins(2, 0, 2, 0)
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            f"font-size:10px;font-weight:600;color:{GRAY_700};"
            f"background:transparent;border:none;"
        )
        name_lbl.setWordWrap(False)
        status_color = EMERALD_400 if status == "Annotated" else GRAY_400
        dot = QLabel("●")
        dot.setStyleSheet(
            f"font-size:8px;color:{status_color};background:transparent;border:none;"
        )
        name_row.addWidget(name_lbl, 1)
        name_row.addWidget(dot)
        root.addLayout(name_row)

    def _update_style(self, selected: bool):
        if selected:
            self.setStyleSheet(f"""
                QWidget#ImageCard {{
                    background: {VIOLET_50};
                    border: 2px solid {VIOLET_600};
                    border-radius: 10px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget#ImageCard {{
                    background: {WHITE};
                    border: 1px solid {GRAY_200};
                    border-radius: 10px;
                }}
                QWidget#ImageCard:hover {{
                    border-color: #C4B5FD;
                }}
            """)

    def set_selected(self, selected: bool):
        self._selected = selected
        self._update_style(selected)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._selected = not self._selected
                self._update_style(self._selected)
                self.toggled.emit(self._image_id, self._selected)
            else:
                self.clicked.emit(self._image_id)

    @property
    def image_id(self):
        return self._image_id
