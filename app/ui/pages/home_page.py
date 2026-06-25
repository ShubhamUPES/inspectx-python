import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QScrollArea, QFrame, QGridLayout,
    QDialog, QButtonGroup, QRadioButton, QSizePolicy, QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QColor

from app.ui.theme import (
    WHITE, GRAY_50, GRAY_100, GRAY_200, GRAY_300, GRAY_400, GRAY_500,
    GRAY_700, GRAY_900, VIOLET_50, VIOLET_100, VIOLET_200, VIOLET_400,
    VIOLET_500, VIOLET_600, CYAN_50, CYAN_600, EMERALD_50, EMERALD_600,
    INDIGO_50, INDIGO_600, CONTENT_BG,
)
from app.ui.widgets.badge import Badge
from app.ui.widgets.toast import Toast

LOGO_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "hestabit-logo.jpg")
)

TYPE_OPTIONS = {
    "detection": {
        "label": "Object Detection",
        "badge": "Bounding Boxes",
        "desc": "Bounding boxes and defect position detection.",
        "enabled": "bbox, count, tracking",
        "disabled": "polygon, brush",
    },
    "segmentation": {
        "label": "Instance Segmentation",
        "badge": "Polygon Masks",
        "desc": "Polygon masks and surface defect segmentation.",
        "enabled": "polygon, brush, mask",
        "disabled": "bbox, count, tracking",
    },
}


class CreateProjectDialog(QDialog):
    created = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setMinimumWidth(560)
        self.setStyleSheet(f"background:{WHITE};")
        self._selected_type = "detection"
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header
        title = QLabel("Create new project")
        title.setStyleSheet(f"font-size:18px;font-weight:800;color:{GRAY_900};")
        sub = QLabel("Give it a name and pick the inspection type.")
        sub.setStyleSheet(f"font-size:12px;color:{GRAY_500};")
        layout.addWidget(title)
        layout.addWidget(sub)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{GRAY_200};background:{GRAY_200};border:none;max-height:1px;")
        layout.addWidget(sep)

        # Name
        name_lbl = QLabel("Project Name")
        name_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{GRAY_700};")
        layout.addWidget(name_lbl)
        self._name_input = QLineEdit("Defect Detection System")
        self._name_input.setStyleSheet(f"""
            QLineEdit {{
                background:{GRAY_50};border:1px solid {GRAY_200};
                border-radius:10px;padding:10px 14px;
                font-size:13px;color:{GRAY_900};
            }}
            QLineEdit:focus {{
                border-color:{VIOLET_500};background:{WHITE};
            }}
        """)
        self._name_input.setFixedHeight(44)
        layout.addWidget(self._name_input)

        # Type selection
        type_lbl = QLabel("Inspection Type")
        type_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{GRAY_700};")
        layout.addWidget(type_lbl)

        type_grid = QHBoxLayout()
        type_grid.setSpacing(12)
        self._type_cards: dict[str, QWidget] = {}
        for tid, cfg in TYPE_OPTIONS.items():
            card = self._make_type_card(tid, cfg)
            self._type_cards[tid] = card
            type_grid.addWidget(card)
        layout.addLayout(type_grid)

        self._refresh_type_cards()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background:{WHITE};color:{GRAY_700};
                border:1px solid {GRAY_200};border-radius:10px;
                padding:8px 18px;font-size:13px;font-weight:600;
            }}
            QPushButton:hover {{ background:{GRAY_50}; }}
        """)
        cancel_btn.clicked.connect(self.reject)
        create_btn = QPushButton("✦  Create Project")
        create_btn.setStyleSheet(f"""
            QPushButton {{
                background:{VIOLET_600};color:{WHITE};
                border:none;border-radius:10px;
                padding:8px 20px;font-size:13px;font-weight:700;
            }}
            QPushButton:hover {{ background:{VIOLET_500}; }}
            QPushButton:disabled {{ background:{GRAY_300};color:{GRAY_500}; }}
        """)
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(self._on_create)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(create_btn)
        layout.addLayout(btn_row)

    def _make_type_card(self, tid: str, cfg: dict) -> QWidget:
        card = QWidget()
        card.setObjectName(f"TypeCard_{tid}")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 14, 14, 14)
        cl.setSpacing(6)
        badge = Badge(cfg["badge"], "purple" if tid == "detection" else "cyan")
        title = QLabel(cfg["label"])
        title.setStyleSheet(f"font-size:15px;font-weight:800;color:{GRAY_900};background:transparent;border:none;")
        desc = QLabel(cfg["desc"])
        desc.setStyleSheet(f"font-size:11px;color:{GRAY_500};background:transparent;border:none;")
        desc.setWordWrap(True)
        enabled = QLabel(f"✓  {cfg['enabled']}")
        enabled.setStyleSheet(f"font-size:10px;color:#059669;background:transparent;border:none;")
        disabled = QLabel(f"—  {cfg['disabled']}")
        disabled.setStyleSheet(f"font-size:10px;color:#EF4444;background:transparent;border:none;")
        cl.addWidget(badge)
        cl.addWidget(title)
        cl.addWidget(desc)
        cl.addWidget(enabled)
        cl.addWidget(disabled)

        def _click(event, t=tid):
            self._selected_type = t
            self._refresh_type_cards()

        card.mousePressEvent = _click
        return card

    def _refresh_type_cards(self):
        for tid, card in self._type_cards.items():
            if tid == self._selected_type:
                card.setStyleSheet(f"""
                    QWidget {{
                        background:{VIOLET_50};border:2px solid {VIOLET_500};border-radius:14px;
                    }}
                """)
            else:
                card.setStyleSheet(f"""
                    QWidget {{
                        background:{GRAY_50};border:1px solid {GRAY_200};border-radius:14px;
                    }}
                    QWidget:hover {{
                        background:{WHITE};border-color:{GRAY_300};
                    }}
                """)

    def _on_create(self):
        name = self._name_input.text().strip()
        if name:
            self.created.emit(name, self._selected_type)
            self.accept()


class ProjectCard(QWidget):
    open_project = pyqtSignal(int)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self._project_id = project.id
        self.setObjectName("ProjectCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build(project)
        self._update_style(False)

    def _build(self, p):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Colour banner
        banner = QWidget()
        banner.setFixedHeight(80)
        colors = {
            "detection":    "#1e1b4b",
            "segmentation": "#0c4a6e",
        }
        banner.setStyleSheet(
            f"background:{colors.get(p.type, '#1e1b4b')};"
            f"border-radius:14px 14px 0 0;"
        )
        bl = QHBoxLayout(banner)
        bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        type_lbl = QLabel(p.type.upper())
        type_lbl.setStyleSheet(
            f"font-size:10px;font-weight:700;letter-spacing:0.15em;"
            f"color:rgba(255,255,255,0.3);background:transparent;border:none;"
        )
        bl.addWidget(type_lbl)
        layout.addWidget(banner)

        # Body
        body = QWidget()
        body.setStyleSheet("background:transparent;border:none;")
        bl2 = QVBoxLayout(body)
        bl2.setContentsMargins(16, 14, 16, 14)
        bl2.setSpacing(6)

        name_row = QHBoxLayout()
        name_lbl = QLabel(p.name)
        name_lbl.setStyleSheet(
            f"font-size:14px;font-weight:700;color:{GRAY_900};"
            f"background:transparent;border:none;"
        )
        type_badge = Badge(
            "Object Detection" if p.type == "detection" else "Instance Segmentation",
            "purple" if p.type == "detection" else "cyan"
        )
        name_row.addWidget(name_lbl, 1)
        name_row.addWidget(type_badge)
        bl2.addLayout(name_row)

        updated = QLabel(f"Updated {p.updated_str()}")
        updated.setStyleSheet(f"font-size:10px;color:{GRAY_400};background:transparent;border:none;")
        bl2.addWidget(updated)

        # Progress bar
        annotated = p.annotated_count()
        total = len(p.images)
        pct = int((annotated / total * 100)) if total else 0

        prog_lbl_row = QHBoxLayout()
        prog_lbl_row.addWidget(QLabel("Annotated") if True else None)
        ann_lbl = QLabel("Annotated")
        ann_lbl.setStyleSheet(f"font-size:11px;color:{GRAY_500};background:transparent;border:none;")
        count_lbl = QLabel(f"{annotated}/{total}")
        count_lbl.setStyleSheet(f"font-size:11px;font-weight:600;color:{GRAY_700};background:transparent;border:none;")
        prog_lbl_row.addWidget(ann_lbl)
        prog_lbl_row.addStretch()
        prog_lbl_row.addWidget(count_lbl)
        bl2.addLayout(prog_lbl_row)

        bar_bg = QWidget()
        bar_bg.setFixedHeight(6)
        bar_bg.setStyleSheet(f"background:{GRAY_100};border-radius:3px;")
        bar_inner = QWidget(bar_bg)
        bar_inner.setFixedHeight(6)
        bar_inner.setStyleSheet(f"background:{VIOLET_600};border-radius:3px;")
        bar_inner.setFixedWidth(max(0, int(pct / 100 * 220)))
        bl2.addWidget(bar_bg)

        # Stats row
        stats_row = QHBoxLayout()
        img_badge = Badge(f"{total} images", "gray")
        model_badge = Badge(f"{len(p.ml_models)} models", "cyan")
        stats_row.addWidget(img_badge)
        stats_row.addWidget(model_badge)
        stats_row.addStretch()
        bl2.addLayout(stats_row)

        layout.addWidget(body)

        # Footer
        footer = QWidget()
        footer.setStyleSheet(
            f"background:{GRAY_50};border-top:1px solid {GRAY_100};"
            f"border-radius:0 0 14px 14px;"
        )
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(16, 8, 16, 8)
        open_lbl = QLabel("Open project →")
        open_lbl.setStyleSheet(
            f"font-size:11px;font-weight:600;color:{VIOLET_600};"
            f"background:transparent;border:none;"
        )
        fl.addStretch()
        fl.addWidget(open_lbl)
        layout.addWidget(footer)

    def _update_style(self, hovered: bool):
        if hovered:
            self.setStyleSheet(f"""
                QWidget#ProjectCard {{
                    background:{WHITE};
                    border:1px solid {VIOLET_200};
                    border-radius:16px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget#ProjectCard {{
                    background:{WHITE};
                    border:1px solid {GRAY_200};
                    border-radius:16px;
                }}
            """)

    def enterEvent(self, event):
        self._update_style(True)

    def leaveEvent(self, event):
        self._update_style(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_project.emit(self._project_id)


class HomePage(QWidget):
    open_project = pyqtSignal(int)
    create_project = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        self._projects = []
        self._search = ""
        self._filter = "All"
        self._sort = "Updated"
        self._toast = Toast(self)
        self._build()

    def set_user(self, user):
        self._user = user

    def load_projects(self, projects: list):
        self._projects = projects
        self._refresh_list()

    def notify(self, msg: str):
        self._toast.show_message(msg)

    def _build(self):
        self.setStyleSheet(f"background:{CONTENT_BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_body(), 1)

    def _build_header(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(60)
        bar.setStyleSheet(f"""
            background:{WHITE};
            border-bottom:1px solid {GRAY_200};
        """)
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(32, 0, 32, 0)

        logo = QLabel()
        if os.path.exists(LOGO_PATH):
            px = QPixmap(LOGO_PATH).scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(px)
        logo.setStyleSheet("background:transparent;border:none;")
        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        b1 = QLabel("Hestabit Defect Detection Studio")
        b1.setStyleSheet(f"font-size:13px;font-weight:700;color:{GRAY_900};background:transparent;border:none;")
        b2 = QLabel("Workspace")
        b2.setStyleSheet(f"font-size:11px;color:{GRAY_400};background:transparent;border:none;")
        brand_col.addWidget(b1)
        brand_col.addWidget(b2)

        hl.addWidget(logo)
        hl.addSpacing(10)
        hl.addLayout(brand_col)
        hl.addStretch()

        self._project_count_badge = QLabel("")
        self._project_count_badge.setStyleSheet(f"""
            background:{GRAY_50};border:1px solid {GRAY_200};
            border-radius:8px;padding:4px 12px;
            font-size:12px;font-weight:600;color:{GRAY_700};
        """)
        hl.addWidget(self._project_count_badge)
        hl.addSpacing(10)

        new_btn = QPushButton("+ New Project")
        new_btn.setFixedHeight(36)
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background:{VIOLET_600};color:{WHITE};
                border:none;border-radius:10px;
                padding:0 16px;font-size:12px;font-weight:700;
            }}
            QPushButton:hover {{ background:{VIOLET_500}; }}
        """)
        new_btn.clicked.connect(self._open_create_dialog)
        hl.addWidget(new_btn)
        return bar

    def _build_body(self) -> QWidget:
        body = QWidget()
        bl = QVBoxLayout(body)
        bl.setContentsMargins(32, 24, 32, 24)
        bl.setSpacing(16)

        # Stats strip
        self._stats_strip = QWidget()
        ss = QHBoxLayout(self._stats_strip)
        ss.setContentsMargins(0, 0, 0, 0)
        ss.setSpacing(12)
        self._stat_cards = {}
        for label, key, bg, fg in [
            ("Total Projects", "projects", VIOLET_50, VIOLET_600),
            ("Total Images",   "images",   CYAN_50,   CYAN_600),
            ("Trained Models", "models",   INDIGO_50, INDIGO_600),
            ("Active Projects","active",   EMERALD_50, EMERALD_600),
        ]:
            sc = QWidget()
            sc.setStyleSheet(f"""
                QWidget {{
                    background:{WHITE};border:1px solid {GRAY_200};
                    border-radius:14px;
                }}
            """)
            scl = QHBoxLayout(sc)
            scl.setContentsMargins(16, 14, 16, 14)
            scl.setSpacing(12)
            icon_box = QWidget()
            icon_box.setFixedSize(40, 40)
            icon_box.setStyleSheet(f"background:{bg};border-radius:10px;border:none;")
            icon_lbl = QLabel({"projects":"📁","images":"🖼","models":"⚡","active":"📊"}[key])
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet("background:transparent;border:none;font-size:16px;")
            ibl = QVBoxLayout(icon_box)
            ibl.setContentsMargins(0,0,0,0)
            ibl.addWidget(icon_lbl)
            text_col = QVBoxLayout()
            text_col.setSpacing(0)
            l_lbl = QLabel(label)
            l_lbl.setStyleSheet(f"font-size:10px;color:{GRAY_500};background:transparent;border:none;")
            v_lbl = QLabel("0")
            v_lbl.setStyleSheet(f"font-size:22px;font-weight:800;color:{GRAY_900};background:transparent;border:none;")
            text_col.addWidget(l_lbl)
            text_col.addWidget(v_lbl)
            scl.addWidget(icon_box)
            scl.addLayout(text_col)
            scl.addStretch()
            ss.addWidget(sc, 1)
            self._stat_cards[key] = v_lbl

        bl.addWidget(self._stats_strip)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        section_title = QVBoxLayout()
        st = QLabel("ALL PROJECTS")
        st.setStyleSheet(f"font-size:11px;font-weight:700;letter-spacing:0.1em;color:{GRAY_500};background:transparent;border:none;")
        self._showing_lbl = QLabel("")
        self._showing_lbl.setStyleSheet(f"font-size:10px;color:{GRAY_400};background:transparent;border:none;")
        section_title.addWidget(st)
        section_title.addWidget(self._showing_lbl)
        toolbar.addLayout(section_title)
        toolbar.addStretch()

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search projects…")
        self._search_input.setFixedWidth(200)
        self._search_input.setFixedHeight(34)
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background:{WHITE};border:1px solid {GRAY_200};
                border-radius:10px;padding:0 12px;
                font-size:12px;color:{GRAY_900};
            }}
            QLineEdit:focus {{ border-color:{VIOLET_400}; }}
        """)
        self._search_input.textChanged.connect(self._on_search)

        self._filter_combo = QComboBox()
        self._filter_combo.addItems(["All", "Object Detection", "Instance Segmentation"])
        self._filter_combo.setFixedHeight(34)
        self._filter_combo.setStyleSheet(f"""
            QComboBox {{
                background:{WHITE};border:1px solid {GRAY_200};
                border-radius:10px;padding:0 10px;
                font-size:12px;color:{GRAY_700};
            }}
            QComboBox:focus {{ border-color:{VIOLET_400}; }}
        """)
        self._filter_combo.currentTextChanged.connect(self._on_filter)

        self._sort_combo = QComboBox()
        self._sort_combo.addItems(["Updated", "Name", "Images"])
        self._sort_combo.setFixedHeight(34)
        self._sort_combo.setStyleSheet(self._filter_combo.styleSheet())
        self._sort_combo.currentTextChanged.connect(self._on_sort)

        toolbar.addWidget(self._search_input)
        toolbar.addWidget(self._filter_combo)
        toolbar.addWidget(self._sort_combo)
        bl.addLayout(toolbar)

        # Grid container (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent;border:none;")
        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background:transparent;")
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(16)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self._grid_widget)
        bl.addWidget(scroll, 1)

        # Empty state
        self._empty_lbl = QLabel("No projects yet.\nClick '+ New Project' to get started.")
        self._empty_lbl.setStyleSheet(
            f"font-size:14px;color:{GRAY_400};background:transparent;border:none;"
        )
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.hide()
        bl.addWidget(self._empty_lbl)

        return body

    def _refresh_list(self):
        projects = self._visible_projects()

        # Update stats
        total_images = sum(len(p.images) for p in self._projects)
        total_models = sum(len(p.ml_models) for p in self._projects)
        active = sum(1 for p in self._projects if p.status == "Active")
        self._stat_cards["projects"].setText(str(len(self._projects)))
        self._stat_cards["images"].setText(str(total_images))
        self._stat_cards["models"].setText(str(total_models))
        self._stat_cards["active"].setText(str(active))
        self._project_count_badge.setText(f"📁  {len(self._projects)} Projects")
        self._showing_lbl.setText(f"Showing {len(projects)} project(s)")

        # Clear grid
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not projects:
            self._empty_lbl.show()
            return
        self._empty_lbl.hide()

        cols = 3
        for i, p in enumerate(projects):
            row, col = divmod(i, cols)
            card = ProjectCard(p)
            card.open_project.connect(self.open_project)
            self._grid_layout.addWidget(card, row, col)

        # Fill remaining cells with stretch
        total = len(projects)
        remainder = cols - (total % cols)
        if remainder < cols:
            row = (total - 1) // cols
            for c in range(total % cols, cols):
                spacer = QWidget()
                spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self._grid_layout.addWidget(spacer, row, c)

    def _visible_projects(self) -> list:
        result = list(self._projects)
        if self._search:
            result = [p for p in result if self._search.lower() in p.name.lower()]
        if self._filter != "All":
            type_map = {"Object Detection": "detection", "Instance Segmentation": "segmentation"}
            t = type_map.get(self._filter)
            if t:
                result = [p for p in result if p.type == t]
        if self._sort == "Name":
            result.sort(key=lambda p: p.name)
        elif self._sort == "Images":
            result.sort(key=lambda p: len(p.images), reverse=True)
        return result

    def _on_search(self, text: str):
        self._search = text
        self._refresh_list()

    def _on_filter(self, text: str):
        self._filter = text
        self._refresh_list()

    def _on_sort(self, text: str):
        self._sort = text
        self._refresh_list()

    def _open_create_dialog(self):
        dlg = CreateProjectDialog(self)
        dlg.created.connect(self.create_project)
        dlg.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._toast._reposition()
