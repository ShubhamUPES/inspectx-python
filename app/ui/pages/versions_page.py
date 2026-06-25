from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QCheckBox, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.ui.theme import (
    WHITE, GRAY_50, GRAY_100, GRAY_200, GRAY_400, GRAY_500,
    GRAY_700, GRAY_900, VIOLET_50, VIOLET_200, VIOLET_600,
    EMERALD_50, EMERALD_200, EMERALD_600, AMBER_50, AMBER_200, AMBER_600,
    CONTENT_BG,
)
from app.ui.widgets.card import Card
from app.ui.widgets.metric_card import MetricCard
from app.ui.widgets.badge import Badge

AUGMENTATION_OPTIONS = [
    "resize", "auto orient", "CLAHE", "crop", "contrast", "denoise",
    "flip", "rotate", "blur", "noise", "HSV", "mosaic",
    "motion blur", "cutout", "brightness", "exposure",
]


class VersionsPage(QWidget):
    navigate = pyqtSignal(str)

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

        self._main_card = Card("Dataset Versions", "Generate versions before training.", "purple")
        self._builder_card = Card("Version Builder", "Preprocessing, augmentation, and transforms.", "amber")
        self._builder_card.setFixedWidth(300)

        root.addWidget(self._main_card, 1)
        root.addWidget(self._builder_card)

        self._build_builder()
        self.refresh()

    def _build_builder(self):
        cl = self._builder_card.content_layout()
        cl.setSpacing(8)

        p = self._state.project
        total = len(p.images) if p else 0

        for lbl, val, tone in [
            ("Raw Images", str(total), "gray"),
            ("Generated Count", str(total * 3) if total else "0", "green"),
            ("Resize", "640 px", "purple"),
        ]:
            cl.addWidget(MetricCard(lbl, val, tone))

        aug_lbl = QLabel("Augmentation & Preprocessing")
        aug_lbl.setStyleSheet(f"font-size:12px;font-weight:600;color:{GRAY_900};background:transparent;border:none;")
        cl.addWidget(aug_lbl)

        grid_w = QWidget()
        grid_w.setStyleSheet("background:transparent;border:none;")
        gl = QGridLayout(grid_w)
        gl.setSpacing(4)
        gl.setContentsMargins(0, 0, 0, 0)
        checked_default = {"resize", "auto orient", "flip", "rotate", "brightness"}
        for i, opt in enumerate(AUGMENTATION_OPTIONS):
            row, col = divmod(i, 2)
            cb = QCheckBox(opt)
            cb.setChecked(opt in checked_default)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    font-size:11px;color:{GRAY_700};background:transparent;
                    border:1px solid {GRAY_200};border-radius:6px;padding:4px 6px;
                }}
                QCheckBox:checked {{ background:{VIOLET_50};border-color:{VIOLET_200}; }}
            """)
            gl.addWidget(cb, row, col)
        cl.addWidget(grid_w)

    def refresh(self):
        cl = self._main_card.content_layout()
        while cl.count():
            item = cl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        p = self._state.project
        if not p:
            return

        # Actions — use a proper QWidget container so clearing works
        act_w = QWidget()
        act_w.setStyleSheet("background:transparent;border:none;")
        act_row = QHBoxLayout(act_w)
        act_row.setContentsMargins(0, 0, 0, 0)
        act_row.setSpacing(8)
        gen_btn = QPushButton("Generate Version")
        gen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gen_btn.setStyleSheet(f"""
            QPushButton {{
                background:{EMERALD_50};color:{EMERALD_600};
                border:1px solid {EMERALD_200};border-radius:9px;
                padding:8px 16px;font-size:12px;font-weight:600;
            }}
            QPushButton:hover {{ background:#D1FAE5; }}
        """)
        gen_btn.clicked.connect(self._state.generate_version)
        go_train = QPushButton("Go to Training")
        go_train.setCursor(Qt.CursorShape.PointingHandCursor)
        go_train.setStyleSheet(f"""
            QPushButton {{
                background:{WHITE};color:{GRAY_700};
                border:1px solid {GRAY_200};border-radius:9px;
                padding:8px 16px;font-size:12px;font-weight:600;
            }}
            QPushButton:hover {{ background:{GRAY_50}; }}
        """)
        go_train.clicked.connect(lambda: self.navigate.emit("train"))
        act_row.addWidget(gen_btn)
        act_row.addWidget(go_train)
        act_row.addStretch()
        cl.addWidget(act_w)

        if not p.versions:
            empty = QLabel("No dataset versions yet.\nGenerate a version before training.")
            empty.setStyleSheet(f"font-size:12px;color:{GRAY_400};background:transparent;border:none;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(empty)
            cl.addStretch()
            return

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent;border:none;")
        vw = QWidget()
        vw.setStyleSheet("background:transparent;")
        vl = QVBoxLayout(vw)
        vl.setSpacing(10)
        vl.setContentsMargins(0, 0, 0, 0)

        active_v = self._state.active_version()

        for v in p.versions:
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background:{GRAY_50};border:1px solid {GRAY_200};border-radius:12px;
                }}
            """)
            vcl = QVBoxLayout(card)
            vcl.setContentsMargins(14, 12, 14, 12)
            vcl.setSpacing(8)

            hdr = QHBoxLayout()
            name_col = QVBoxLayout()
            name_col.setSpacing(1)
            nlbl = QLabel(v.name)
            nlbl.setStyleSheet(f"font-size:13px;font-weight:700;color:{GRAY_900};background:transparent;border:none;")
            dlbl = QLabel(
                f"Frozen {v.created_str()} · Raw {v.image_count} · "
                f"Annotated {v.annotated_count} · Generated {v.generated_count}"
            )
            dlbl.setStyleSheet(f"font-size:10px;color:{GRAY_500};background:transparent;border:none;")
            name_col.addWidget(nlbl)
            name_col.addWidget(dlbl)
            hdr.addLayout(name_col, 1)
            is_active = (active_v and active_v.id == v.id)
            hdr.addWidget(Badge("Active" if is_active else "Version", "green" if is_active else "gray"))
            vcl.addLayout(hdr)

            metrics_row = QHBoxLayout()
            metrics_row.setSpacing(6)
            metrics_row.addWidget(MetricCard("Preprocessing", ", ".join(v.preprocessing[:2]), "gray"))
            metrics_row.addWidget(MetricCard("Augmentation", ", ".join(v.augmentation[:2]), "amber"))
            vcl.addLayout(metrics_row)

            btn_row = QHBoxLayout()
            btn_row.setSpacing(6)
            for blbl, bcallback in [
                ("Train From This", lambda checked, vid=v.id, vn=v.name: self._train_from(vid, vn)),
                ("Export Dataset",  lambda: self._state.notify("Dataset export coming soon.")),
            ]:
                b = QPushButton(blbl)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.setStyleSheet(f"""
                    QPushButton {{
                        background:{WHITE};color:{GRAY_700};
                        border:1px solid {GRAY_200};border-radius:8px;
                        padding:5px 12px;font-size:11px;font-weight:600;
                    }}
                    QPushButton:hover {{ background:{GRAY_50}; }}
                """)
                b.clicked.connect(bcallback)
                btn_row.addWidget(b)
            btn_row.addStretch()
            vcl.addLayout(btn_row)
            vl.addWidget(card)

        vl.addStretch()
        scroll.setWidget(vw)
        cl.addWidget(scroll, 1)

    def _train_from(self, version_id: int, version_name: str):
        self._state.set_active_version(version_id)
        self.navigate.emit("train")
