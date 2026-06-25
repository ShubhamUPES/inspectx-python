from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.ui.theme import WHITE, GRAY_50, GRAY_200, GRAY_400, GRAY_500, GRAY_900, VIOLET_600, VIOLET_50, VIOLET_200


ROUTE_TITLES = {
    "overview": "Project Overview",
    "upload":   "Upload Data",
    "annotate": "Annotate",
    "dataset":  "Dataset",
    "versions": "Dataset Versions",
    "classes":  "Classes & Tags",
    "train":    "Train Model",
    "models":   "Models",
    "test":     "Test",
    "settings": "Settings",
}

ROUTE_ICONS = {
    "overview": "◈",
    "upload":   "↑",
    "annotate": "✎",
    "dataset":  "⊟",
    "versions": "⊞",
    "classes":  "◉",
    "train":    "⚡",
    "models":   "◫",
    "test":     "▶",
    "settings": "⚙",
}


class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self.setStyleSheet(f"""
            QWidget {{
                background: {WHITE};
                border-bottom: 1px solid {GRAY_200};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        # Icon badge
        self._icon_badge = QLabel("")
        self._icon_badge.setFixedSize(32, 32)
        self._icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_badge.setStyleSheet(
            f"background:{VIOLET_50};border:1px solid {VIOLET_200};"
            f"border-radius:9px;font-size:14px;color:{VIOLET_600};"
        )

        self._title_lbl = QLabel("")
        self._title_lbl.setStyleSheet(
            f"font-size:16px;font-weight:700;color:{GRAY_900};"
            f"background:transparent;border:none;"
        )

        self._project_lbl = QLabel("")
        self._project_lbl.setStyleSheet(
            f"font-size:11px;color:{GRAY_400};"
            f"background:{GRAY_50};border:1px solid {GRAY_200};"
            f"border-radius:8px;padding:3px 10px;"
        )

        layout.addWidget(self._icon_badge)
        layout.addWidget(self._title_lbl)
        layout.addStretch()
        layout.addWidget(self._project_lbl)

    def set_route(self, route: str, project_name: str = ""):
        title = ROUTE_TITLES.get(route, route.capitalize())
        icon = ROUTE_ICONS.get(route, "●")
        self._icon_badge.setText(icon)
        self._title_lbl.setText(title)
        if project_name:
            self._project_lbl.setText(f"  {project_name}  ")
            self._project_lbl.show()
        else:
            self._project_lbl.hide()
