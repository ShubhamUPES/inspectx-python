from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from app.ui.theme import (
    DARK_BG, SIDEBAR_BORDER, VIOLET_600, VIOLET_400, VIOLET_200,
    GRAY_400, GRAY_600, GRAY_700, WHITE,
    CYAN_500, AMBER_600,
)
import os

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "hestabit-logo.jpg")

NAV_GROUPS = [
    {
        "label": "Data",
        "color": "#22D3EE",
        "links": [
            ("upload",   "Upload Data"),
            ("annotate", "Annotate"),
            ("dataset",  "Dataset"),
            ("versions", "Versions"),
            ("classes",  "Classes & Tags"),
        ],
    },
    {
        "label": "Models",
        "color": "#A78BFA",
        "links": [
            ("train",  "Train"),
            ("models", "Models"),
            ("test",   "Test"),
        ],
    },
]


class SidebarButton(QPushButton):
    def __init__(self, route_id: str, label: str, parent=None):
        super().__init__(label, parent)
        self.route_id = route_id
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_inactive()

    def _set_active(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {VIOLET_600};
                color: {WHITE};
                border: none;
                border-radius: 9px;
                padding: 9px 14px;
                text-align: left;
                font-size: 12px;
                font-weight: 600;
            }}
        """)

    def _set_inactive(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 9px;
                padding: 9px 14px;
                text-align: left;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.07);
                color: {WHITE};
            }}
        """)

    def set_active(self, active: bool):
        if active:
            self._set_active()
        else:
            self._set_inactive()


class ProjectSidebar(QWidget):
    route_changed = pyqtSignal(str)
    back_home = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_route = "overview"
        self._buttons: dict[str, SidebarButton] = {}
        self._project_name = ""
        self._project_type = ""
        self._build()
        self.setFixedWidth(232)

    def _build(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {DARK_BG};
                border-right: 1px solid {SIDEBAR_BORDER};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Brand bar ──────────────────────────────────────
        brand = QWidget()
        brand.setFixedHeight(68)
        brand.setStyleSheet(f"background:{DARK_BG};border-bottom:1px solid {SIDEBAR_BORDER};")
        bl = QHBoxLayout(brand)
        bl.setContentsMargins(14, 0, 14, 0)
        bl.setSpacing(10)

        logo_lbl = QLabel()
        logo_lbl.setFixedSize(38, 38)
        px = QPixmap(LOGO_PATH)
        if not px.isNull():
            px = px.scaled(38, 38, Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(px)
        logo_lbl.setStyleSheet(
            "border:2px solid rgba(139,92,246,0.4);border-radius:10px;"
            "background:rgba(109,40,217,0.15);"
        )
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        brand_text = QWidget()
        brand_text.setStyleSheet("background:transparent;border:none;")
        btl = QVBoxLayout(brand_text)
        btl.setContentsMargins(0, 0, 0, 0)
        btl.setSpacing(1)
        n = QLabel("Hestabit DDS")
        n.setStyleSheet(
            f"font-size:12px;font-weight:700;color:{WHITE};"
            f"background:transparent;border:none;letter-spacing:0.01em;"
        )
        s = QLabel("Defect Detection Studio")
        s.setStyleSheet(
            f"font-size:9px;color:{VIOLET_400};background:transparent;border:none;"
        )
        btl.addWidget(n)
        btl.addWidget(s)

        bl.addWidget(logo_lbl)
        bl.addWidget(brand_text)
        bl.addStretch()
        root.addWidget(brand)

        # ── Scrollable nav ─────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background:transparent;border:none;")

        nav_widget = QWidget()
        nav_widget.setStyleSheet(f"background:{DARK_BG};")
        nav = QVBoxLayout(nav_widget)
        nav.setContentsMargins(8, 8, 8, 8)
        nav.setSpacing(2)

        # Back button
        back_btn = QPushButton("← Projects")
        back_btn.setFlat(True)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {GRAY_600};
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                text-align: left;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.05);
                color: {GRAY_400};
            }}
        """)
        back_btn.clicked.connect(self.back_home)
        nav.addWidget(back_btn)

        # Project info box
        self._project_box = QWidget()
        self._project_box.setStyleSheet(f"""
            QWidget {{
                background: rgba(109,40,217,0.15);
                border: 1px solid rgba(109,40,217,0.3);
                border-radius: 10px;
            }}
        """)
        pbl = QVBoxLayout(self._project_box)
        pbl.setContentsMargins(10, 8, 10, 8)
        pbl.setSpacing(2)
        proj_tag = QLabel("ACTIVE PROJECT")
        proj_tag.setStyleSheet(
            f"font-size:8px;font-weight:700;color:{VIOLET_400};"
            f"letter-spacing:0.1em;background:transparent;border:none;"
        )
        self._proj_name_lbl = QLabel("")
        self._proj_name_lbl.setStyleSheet(
            f"font-size:11px;font-weight:700;color:{WHITE};"
            f"background:transparent;border:none;"
        )
        self._proj_name_lbl.setWordWrap(True)
        self._proj_type_lbl = QLabel("")
        self._proj_type_lbl.setStyleSheet(
            f"font-size:9px;color:{VIOLET_400};background:transparent;border:none;"
        )
        pbl.addWidget(proj_tag)
        pbl.addWidget(self._proj_name_lbl)
        pbl.addWidget(self._proj_type_lbl)
        nav.addWidget(self._project_box)
        nav.addSpacing(4)

        # Overview
        overview_btn = SidebarButton("overview", "Overview")
        overview_btn.clicked.connect(lambda: self._navigate("overview"))
        self._buttons["overview"] = overview_btn
        nav.addWidget(overview_btn)

        # Groups
        for grp in NAV_GROUPS:
            grp_label = QLabel(grp["label"])
            grp_label.setStyleSheet(
                f"font-size:9px;font-weight:700;color:{grp['color']};"
                f"letter-spacing:0.1em;background:transparent;border:none;"
                f"padding:8px 12px 2px 12px;"
            )
            nav.addWidget(grp_label)
            for route_id, route_label in grp["links"]:
                btn = SidebarButton(route_id, route_label)
                btn.clicked.connect(lambda checked, r=route_id: self._navigate(r))
                self._buttons[route_id] = btn
                nav.addWidget(btn)

        # Settings
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{SIDEBAR_BORDER};background:{SIDEBAR_BORDER};border:none;max-height:1px;")
        nav.addWidget(sep)
        nav.addSpacing(4)
        settings_btn = SidebarButton("settings", "Settings")
        settings_btn.clicked.connect(lambda: self._navigate("settings"))
        self._buttons["settings"] = settings_btn
        nav.addWidget(settings_btn)

        nav.addStretch()
        scroll.setWidget(nav_widget)
        root.addWidget(scroll)

        # ── Footer ─────────────────────────────────────────
        self._footer = QWidget()
        self._footer.setFixedHeight(44)
        self._footer.setStyleSheet(
            f"background:{DARK_BG};border-top:1px solid {SIDEBAR_BORDER};"
        )
        fl = QHBoxLayout(self._footer)
        fl.setContentsMargins(12, 0, 12, 0)
        self._footer_lbl = QLabel("")
        self._footer_lbl.setStyleSheet(
            f"font-size:10px;color:{GRAY_600};background:transparent;border:none;"
        )
        fl.addWidget(self._footer_lbl)
        root.addWidget(self._footer)

        self._navigate("overview")

    def _navigate(self, route: str):
        for r, btn in self._buttons.items():
            btn.set_active(r == route)
        self._current_route = route
        self.route_changed.emit(route)

    def set_project(self, name: str, type_label: str):
        self._proj_name_lbl.setText(name)
        self._proj_type_lbl.setText(type_label)
        self._footer_lbl.setText(f"● {name}")

    def set_route(self, route: str):
        """Set active route WITHOUT emitting route_changed (called externally)."""
        for r, btn in self._buttons.items():
            btn.set_active(r == route)
        self._current_route = route
