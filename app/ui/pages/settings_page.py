from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.ui.theme import (
    WHITE, GRAY_50, GRAY_200, GRAY_400, GRAY_500, GRAY_700, GRAY_900,
    VIOLET_50, VIOLET_200, VIOLET_500, VIOLET_600,
    EMERALD_50, EMERALD_200, EMERALD_600,
    RED_50, RED_200, RED_600,
    CONTENT_BG,
)
from app.ui.widgets.card import Card
from app.ui.widgets.metric_card import MetricCard


class SettingsPage(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state = state
        self._build()
        state.project_changed.connect(self.refresh)

    def _build(self):
        self.setStyleSheet(f"background:{CONTENT_BG};")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self._main_card = Card("Project Settings", "Configure project metadata and options.", "purple")
        self._account_card = Card("Account & Storage", "Manage account and storage settings.", "amber")
        self._account_card.setFixedWidth(280)

        root.addWidget(self._main_card, 1)
        root.addWidget(self._account_card)

        self._build_account_panel()
        self.refresh()

    def _build_account_panel(self):
        cl = self._account_card.content_layout()
        cl.setSpacing(10)

        # Storage info
        for lbl, val, tone in [
            ("Storage Used", "0 MB", "gray"),
            ("Images Stored", "0", "green"),
            ("Models Saved", "0", "purple"),
        ]:
            cl.addWidget(MetricCard(lbl, val, tone))

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{GRAY_200};border:none;max-height:1px;")
        cl.addWidget(sep)

        # Account section
        acc_lbl = QLabel("Account")
        acc_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{GRAY_700};background:transparent;border:none;")
        cl.addWidget(acc_lbl)

        self._email_lbl = QLabel("—")
        self._email_lbl.setStyleSheet(f"font-size:11px;color:{GRAY_500};background:transparent;border:none;")
        cl.addWidget(self._email_lbl)

        logout_btn = QPushButton("Log Out")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background:{RED_50};color:{RED_600};
                border:1px solid {RED_200};border-radius:9px;
                padding:8px;font-size:12px;font-weight:600;
            }}
            QPushButton:hover {{ background:#FEE2E2; }}
        """)
        logout_btn.clicked.connect(self.logout_requested.emit)
        cl.addWidget(logout_btn)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"background:{GRAY_200};border:none;max-height:1px;")
        cl.addWidget(sep2)

        # Export section
        export_lbl = QLabel("Export")
        export_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{GRAY_700};background:transparent;border:none;")
        cl.addWidget(export_lbl)

        export_btn = QPushButton("Export Project Data")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background:{GRAY_50};color:{GRAY_700};
                border:1px solid {GRAY_200};border-radius:9px;
                padding:8px;font-size:12px;font-weight:600;
            }}
            QPushButton:hover {{ background:{WHITE}; }}
        """)
        export_btn.clicked.connect(lambda: self._state.notify("Export coming soon."))
        cl.addWidget(export_btn)

        cl.addStretch()

    def refresh(self):
        cl = self._main_card.content_layout()
        while cl.count():
            item = cl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        user = self._state.user
        if user:
            self._email_lbl.setText(user.email)

        p = self._state.project
        if not p:
            placeholder = QLabel("Open a project to manage its settings.")
            placeholder.setStyleSheet(f"font-size:12px;color:{GRAY_400};background:transparent;border:none;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(placeholder, 1)
            return

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent;border:none;")
        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        il = QVBoxLayout(inner)
        il.setSpacing(14)
        il.setContentsMargins(0, 0, 0, 0)

        # Project Info
        self._add_section_header(il, "Project Information")
        self._project_name_input = self._add_labeled_input(il, "Project Name", p.name)
        self._project_desc_input = self._add_labeled_input(il, "Description", getattr(p, "description", ""))

        type_box = QWidget()
        type_box.setStyleSheet(f"background:{GRAY_50};border:1px solid {GRAY_200};border-radius:9px;")
        tbl = QVBoxLayout(type_box)
        tbl.setContentsMargins(10, 8, 10, 8)
        tbl.setSpacing(4)
        QLabel_style = f"font-size:10px;color:{GRAY_500};background:transparent;border:none;"
        tl = QLabel("Project Type")
        tl.setStyleSheet(QLabel_style)
        tc = QComboBox()
        tc.addItems(["Detection", "Segmentation"])
        tc.setCurrentText("Detection" if p.type == "detection" else "Segmentation")
        tc.setStyleSheet(f"""
            QComboBox {{
                background:{WHITE};border:1px solid {GRAY_200};
                border-radius:7px;padding:0 8px;font-size:12px;color:{GRAY_700};
            }}
        """)
        tc.setFixedHeight(30)
        tbl.addWidget(tl)
        tbl.addWidget(tc)
        il.addWidget(type_box)

        save_btn = QPushButton("Save Changes")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background:{VIOLET_600};color:white;border:none;
                border-radius:10px;font-size:12px;font-weight:700;
            }}
            QPushButton:hover {{ background:{VIOLET_500}; }}
        """)
        save_btn.clicked.connect(self._save_settings)
        il.addWidget(save_btn)

        self._add_separator(il)

        # Camera Config
        self._add_section_header(il, "Camera Configuration")
        cam = p.camera or {}
        self._cam_make = self._add_labeled_input(il, "Make", cam.get("make", ""))
        self._cam_model_input = self._add_labeled_input(il, "Model", cam.get("model", ""))
        self._cam_resolution = self._add_labeled_input(il, "Resolution", cam.get("resolution", ""))

        cam_save = QPushButton("Save Camera Config")
        cam_save.setCursor(Qt.CursorShape.PointingHandCursor)
        cam_save.setStyleSheet(f"""
            QPushButton {{
                background:{EMERALD_50};color:{EMERALD_600};
                border:1px solid {EMERALD_200};border-radius:9px;
                padding:8px;font-size:12px;font-weight:600;
            }}
            QPushButton:hover {{ background:#D1FAE5; }}
        """)
        cam_save.clicked.connect(self._save_camera)
        il.addWidget(cam_save)

        self._add_separator(il)

        # Danger zone
        self._add_section_header(il, "Danger Zone")
        danger_box = QWidget()
        danger_box.setStyleSheet(f"background:{RED_50};border:1px solid {RED_200};border-radius:10px;")
        dbl = QHBoxLayout(danger_box)
        dbl.setContentsMargins(14, 10, 14, 10)
        dtxt = QLabel("Delete all project data. This cannot be undone.")
        dtxt.setStyleSheet(f"font-size:11px;color:{RED_600};background:transparent;border:none;")
        del_btn = QPushButton("Delete Project")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background:{RED_600};color:white;border:none;
                border-radius:8px;padding:6px 12px;font-size:11px;font-weight:600;
            }}
        """)
        del_btn.clicked.connect(lambda: self._state.notify("Delete project coming soon."))
        dbl.addWidget(dtxt, 1)
        dbl.addWidget(del_btn)
        il.addWidget(danger_box)
        il.addStretch()

        scroll.setWidget(inner)
        cl.addWidget(scroll, 1)

    def _add_section_header(self, layout, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size:13px;font-weight:700;color:{GRAY_900};background:transparent;border:none;")
        layout.addWidget(lbl)

    def _add_separator(self, layout):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{GRAY_200};border:none;max-height:1px;")
        layout.addWidget(sep)

    def _add_labeled_input(self, layout, label, value) -> QLineEdit:
        box = QWidget()
        box.setStyleSheet(f"background:{GRAY_50};border:1px solid {GRAY_200};border-radius:9px;")
        bl = QVBoxLayout(box)
        bl.setContentsMargins(10, 8, 10, 8)
        bl.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size:10px;color:{GRAY_500};background:transparent;border:none;")
        inp = QLineEdit(value)
        inp.setStyleSheet(f"""
            QLineEdit {{
                background:{WHITE};border:1px solid {GRAY_200};
                border-radius:7px;padding:4px 8px;font-size:12px;
            }}
            QLineEdit:focus {{ border-color:{VIOLET_600}; }}
        """)
        inp.setFixedHeight(30)
        bl.addWidget(lbl)
        bl.addWidget(inp)
        layout.addWidget(box)
        return inp

    def _save_settings(self):
        p = self._state.project
        if not p:
            return
        from app.services.project_service import patch_project
        name = self._project_name_input.text().strip()
        if name:
            patch_project(p.id, name=name)
            self._state.reload_project()
            self._state.notify("Project settings saved.")

    def _save_camera(self):
        p = self._state.project
        if not p:
            return
        from app.services.project_service import patch_project
        cam = {
            "make": self._cam_make.text().strip(),
            "model": self._cam_model_input.text().strip(),
            "resolution": self._cam_resolution.text().strip(),
        }
        patch_project(p.id, camera=cam)
        self._state.reload_project()
        self._state.notify("Camera config saved.")
