"""
AnnotatePage — full image annotation UI with toolbox.
"""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QScrollArea, QLineEdit, QComboBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.ui.theme import (
    WHITE, GRAY_50, GRAY_100, GRAY_200, GRAY_400, GRAY_500,
    GRAY_700, GRAY_900, VIOLET_50, VIOLET_200, VIOLET_500, VIOLET_600,
    EMERALD_50, EMERALD_200, EMERALD_600,
    RED_50, RED_200, RED_600,
    AMBER_50, AMBER_600,
    CONTENT_BG,
)
from app.ui.widgets.card import Card
from app.ui.widgets.annotation_canvas import AnnotationCanvas
from app.ui.widgets.image_card import ImageCard

IMG_EXTS = "Images (*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp)"

TOOLS = [
    ("select",   "Select",  "↖"),
    ("bbox",     "BBox",    "□"),
    ("polygon",  "Polygon", "⬡"),
    ("count",    "Count",   "#"),
    ("tracking", "Track",   "⇢"),
    ("roi",      "ROI",     "◎"),
]


class UploadPage(QWidget):
    """Dedicated upload page — drag & drop zone + file picker."""
    navigate = pyqtSignal(str)

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state = state
        self._build()

    def _build(self):
        self.setStyleSheet(f"background:{CONTENT_BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = Card("Upload Images", "Add images to your working dataset.", "green")
        root.addWidget(card)
        cl = card.content_layout()

        # Drop zone
        drop = QLabel("⬆\n\nDrop images here\nor click to browse")
        drop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop.setMinimumHeight(220)
        drop.setStyleSheet(f"""
            QLabel {{
                background:{WHITE};
                border:2px dashed {VIOLET_200};
                border-radius:16px;
                font-size:14px;
                color:{GRAY_400};
            }}
            QLabel:hover {{
                border-color:{VIOLET_500};
                background:{VIOLET_50};
                color:{VIOLET_500};
            }}
        """)
        drop.setCursor(Qt.CursorShape.PointingHandCursor)
        drop.mousePressEvent = lambda e: self._pick_files()
        cl.addWidget(drop, 1)

        # Buttons row
        row = QWidget()
        row.setStyleSheet("background:transparent;border:none;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(8)

        pick_btn = QPushButton("Browse Files")
        pick_btn.setFixedHeight(40)
        pick_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pick_btn.setStyleSheet(f"""
            QPushButton {{
                background:{VIOLET_600};color:white;border:none;
                border-radius:10px;padding:0 20px;
                font-size:12px;font-weight:700;
            }}
            QPushButton:hover {{ background:{VIOLET_500}; }}
        """)
        pick_btn.clicked.connect(self._pick_files)

        ann_btn = QPushButton("Go to Annotate →")
        ann_btn.setFixedHeight(40)
        ann_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ann_btn.setStyleSheet(f"""
            QPushButton {{
                background:{WHITE};color:{GRAY_700};
                border:1px solid {GRAY_200};border-radius:10px;padding:0 20px;
                font-size:12px;font-weight:600;
            }}
            QPushButton:hover {{ background:{GRAY_50}; }}
        """)
        ann_btn.clicked.connect(lambda: self.navigate.emit("annotate"))

        rl.addWidget(pick_btn)
        rl.addWidget(ann_btn)
        rl.addStretch()
        cl.addWidget(row)

    def _pick_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", IMG_EXTS)
        if paths:
            self._state.add_images(paths)
            self._state.notify(f"{len(paths)} image(s) added.")
            self.navigate.emit("annotate")


class AnnotatePage(QWidget):
    navigate = pyqtSignal(str)

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state    = state
        self._tool     = "bbox"
        self._pending_ann_id: int | None = None
        self._build()
        state.project_changed.connect(self._on_project_changed)

    # ── Build ──────────────────────────────────────────────────────────────────

    def _build(self):
        self.setStyleSheet(f"background:{CONTENT_BG};")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left: thumbnail filmstrip
        self._filmstrip = self._make_filmstrip()
        root.addWidget(self._filmstrip)

        # Center: canvas + toolbox
        center = QWidget()
        center.setStyleSheet("background:transparent;border:none;")
        cl = QVBoxLayout(center)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        cl.addWidget(self._make_toolbar())
        self._canvas = AnnotationCanvas()
        self._canvas.annotation_created.connect(self._on_ann_created)
        self._canvas.annotation_changed.connect(self._on_ann_changed)
        self._canvas.annotation_selected.connect(self._on_ann_selected)
        cl.addWidget(self._canvas, 1)
        root.addWidget(center, 1)

        # Right: annotation list + label panel
        self._right_panel = self._make_right_panel()
        root.addWidget(self._right_panel)

        self._load_current_image()

    def _make_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(48)
        bar.setStyleSheet(f"background:{WHITE};border-bottom:1px solid {GRAY_200};")
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(12, 0, 12, 0)
        hl.setSpacing(4)

        self._tool_btns: dict[str, QPushButton] = {}
        for tid, label, icon in TOOLS:
            btn = QPushButton(f"{icon}  {label}")
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, t=tid: self._set_tool(t))
            self._tool_btns[tid] = btn
            hl.addWidget(btn)

        hl.addStretch()

        # Zoom controls
        zm = QPushButton("−")
        zm.setFixedSize(30, 30)
        zm.setCursor(Qt.CursorShape.PointingHandCursor)
        zm.clicked.connect(lambda: self._canvas.set_zoom(self._canvas._zoom - 0.1))
        zp = QPushButton("+")
        zp.setFixedSize(30, 30)
        zp.setCursor(Qt.CursorShape.PointingHandCursor)
        zp.clicked.connect(lambda: self._canvas.set_zoom(self._canvas._zoom + 0.1))
        for b in (zm, zp):
            b.setStyleSheet(f"""
                QPushButton {{
                    background:{GRAY_100};border:1px solid {GRAY_200};
                    border-radius:7px;font-size:14px;font-weight:700;color:{GRAY_700};
                }}
                QPushButton:hover {{ background:{GRAY_200}; }}
            """)
        hl.addWidget(zm)
        hl.addWidget(zp)
        self._set_tool("bbox")
        return bar

    def _set_tool(self, tool: str):
        self._tool = tool
        self._canvas.set_tool(tool)
        for tid, btn in self._tool_btns.items():
            active = tid == tool
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:{''+VIOLET_600 if active else WHITE};
                    color:{'white' if active else GRAY_700};
                    border:1px solid {VIOLET_600 if active else GRAY_200};
                    border-radius:8px;padding:0 10px;font-size:11px;font-weight:600;
                }}
                QPushButton:hover {{
                    background:{VIOLET_50 if not active else VIOLET_500};
                    color:{VIOLET_600 if not active else 'white'};
                }}
            """)

    def _make_filmstrip(self) -> QWidget:
        w = QWidget()
        w.setFixedWidth(110)
        w.setStyleSheet(f"background:{WHITE};border-right:1px solid {GRAY_200};")
        outer = QVBoxLayout(w)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        hdr = QLabel("Images")
        hdr.setFixedHeight(48)
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.setStyleSheet(f"""
            font-size:11px;font-weight:700;color:{GRAY_700};
            background:{WHITE};border-bottom:1px solid {GRAY_200};
        """)
        outer.addWidget(hdr)

        self._filmstrip_scroll = QScrollArea()
        self._filmstrip_scroll.setWidgetResizable(True)
        self._filmstrip_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._filmstrip_scroll.setStyleSheet("background:transparent;border:none;")
        self._filmstrip_inner = QWidget()
        self._filmstrip_inner.setStyleSheet("background:transparent;")
        self._filmstrip_layout = QVBoxLayout(self._filmstrip_inner)
        self._filmstrip_layout.setContentsMargins(6, 6, 6, 6)
        self._filmstrip_layout.setSpacing(6)
        self._filmstrip_scroll.setWidget(self._filmstrip_inner)
        outer.addWidget(self._filmstrip_scroll, 1)

        add_btn = QPushButton("+ Add")
        add_btn.setFixedHeight(32)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background:{VIOLET_50};color:{VIOLET_600};
                border:none;border-top:1px solid {GRAY_200};
                font-size:11px;font-weight:600;border-radius:0;
            }}
            QPushButton:hover {{ background:{VIOLET_200}; }}
        """)
        add_btn.clicked.connect(self._pick_more)
        outer.addWidget(add_btn)
        return w

    def _make_right_panel(self) -> QWidget:
        w = QWidget()
        w.setFixedWidth(220)
        w.setStyleSheet(f"background:{WHITE};border-left:1px solid {GRAY_200};")
        vl = QVBoxLayout(w)
        vl.setContentsMargins(10, 10, 10, 10)
        vl.setSpacing(8)

        ann_hdr = QLabel("Annotations")
        ann_hdr.setStyleSheet(f"font-size:12px;font-weight:700;color:{GRAY_900};background:transparent;border:none;")
        vl.addWidget(ann_hdr)

        self._ann_scroll = QScrollArea()
        self._ann_scroll.setWidgetResizable(True)
        self._ann_scroll.setStyleSheet("background:transparent;border:none;")
        self._ann_inner = QWidget()
        self._ann_inner.setStyleSheet("background:transparent;")
        self._ann_layout = QVBoxLayout(self._ann_inner)
        self._ann_layout.setContentsMargins(0, 0, 0, 0)
        self._ann_layout.setSpacing(4)
        self._ann_scroll.setWidget(self._ann_inner)
        vl.addWidget(self._ann_scroll, 1)

        # Label assignment panel (shown when pending annotation)
        self._label_panel = QWidget()
        self._label_panel.setStyleSheet(
            f"background:{VIOLET_50};border:1px solid {VIOLET_200};border-radius:10px;"
        )
        lpl = QVBoxLayout(self._label_panel)
        lpl.setContentsMargins(10, 10, 10, 10)
        lpl.setSpacing(6)
        lp_title = QLabel("Assign Label")
        lp_title.setStyleSheet(f"font-size:11px;font-weight:700;color:{VIOLET_600};background:transparent;border:none;")
        lpl.addWidget(lp_title)

        self._label_combo = QComboBox()
        self._label_combo.setEditable(True)
        self._label_combo.setFixedHeight(32)
        self._label_combo.setStyleSheet(f"""
            QComboBox {{
                background:{WHITE};border:1px solid {VIOLET_200};
                border-radius:7px;padding:0 8px;font-size:12px;color:{GRAY_900};
            }}
        """)
        lpl.addWidget(self._label_combo)

        assign_btn = QPushButton("✓  Assign")
        assign_btn.setFixedHeight(32)
        assign_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        assign_btn.setStyleSheet(f"""
            QPushButton {{
                background:{VIOLET_600};color:white;border:none;
                border-radius:7px;font-size:11px;font-weight:700;
            }}
            QPushButton:hover {{ background:{VIOLET_500}; }}
        """)
        assign_btn.clicked.connect(self._assign_label)
        self._label_combo.lineEdit().returnPressed.connect(self._assign_label)
        lpl.addWidget(assign_btn)

        cancel_lbl = QPushButton("Cancel")
        cancel_lbl.setFlat(True)
        cancel_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_lbl.setStyleSheet(f"color:{GRAY_400};font-size:10px;background:transparent;border:none;")
        cancel_lbl.clicked.connect(self._cancel_pending)
        lpl.addWidget(cancel_lbl, 0, Qt.AlignmentFlag.AlignRight)
        self._label_panel.hide()
        vl.addWidget(self._label_panel)
        return w

    # ── Data loading ───────────────────────────────────────────────────────────

    def _load_current_image(self):
        img = self._state.get_selected_image()
        if img:
            self._canvas.load_image(img.file_path)
            anns = self._state.get_annotations(img.id)
            self._canvas.set_annotations(anns)
            self._refresh_ann_list(anns)
        else:
            self._canvas.load_image("")
            self._canvas.set_annotations([])
            self._refresh_ann_list([])

    def _refresh_filmstrip(self):
        # Clear
        while self._filmstrip_layout.count():
            item = self._filmstrip_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        p = self._state.project
        if not p:
            self._filmstrip_layout.addStretch()
            return
        selected_id = p.selected_image_id
        for img in p.images:
            card = ImageCard(img.id, img.name, img.file_path, img.status, compact=True)
            card.set_selected(img.id == selected_id)
            card.clicked.connect(self._state.select_image)
            self._filmstrip_layout.addWidget(card)
        self._filmstrip_layout.addStretch()

    def _refresh_ann_list(self, anns: list):
        while self._ann_layout.count():
            item = self._ann_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for ann in anns:
            row = QWidget()
            row.setStyleSheet(f"background:{GRAY_50};border:1px solid {GRAY_200};border-radius:8px;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(8, 5, 8, 5)
            rl.setSpacing(6)
            lbl = ann.get("label") or f"[{ann.get('type', 'bbox')}]"
            t = QLabel(lbl)
            t.setStyleSheet(f"font-size:11px;font-weight:600;color:{GRAY_700};background:transparent;border:none;")
            t.setWordWrap(False)
            del_btn = QPushButton("×")
            del_btn.setFixedSize(20, 20)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background:{RED_50};color:{RED_600};border:none;
                    border-radius:4px;font-size:12px;font-weight:700;
                }}
                QPushButton:hover {{ background:{RED_200}; }}
            """)
            ann_id = ann.get("id", -1)
            del_btn.clicked.connect(lambda checked, aid=ann_id: self._delete_ann(aid))
            rl.addWidget(t, 1)
            rl.addWidget(del_btn)
            self._ann_layout.addWidget(row)

        if not anns:
            empty = QLabel("Draw on the\ncanvas to annotate.")
            empty.setStyleSheet(f"font-size:11px;color:{GRAY_400};background:transparent;border:none;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._ann_layout.addWidget(empty)
        self._ann_layout.addStretch()

    # ── Signals / callbacks ────────────────────────────────────────────────────

    def _on_project_changed(self):
        self._refresh_filmstrip()
        self._load_current_image()

    def _on_ann_created(self, ann_dict: dict):
        img = self._state.get_selected_image()
        if not img:
            return
        ann_id = self._state.add_annotation(
            img.id,
            ann_dict["type"],
            ann_dict["x"], ann_dict["y"], ann_dict["w"], ann_dict["h"],
            ann_dict.get("points"),
        )
        self._pending_ann_id = ann_id
        # Refresh labels in combo
        self._label_combo.clear()
        if self._state.project:
            for lbl in self._state.project.labels:
                self._label_combo.addItem(lbl)
        self._label_panel.show()
        self._load_current_image()

    def _on_ann_changed(self, ann_dict: dict):
        ann_id = ann_dict.get("id")
        if ann_id:
            self._state.update_annotation(
                ann_id,
                ann_dict["x"], ann_dict["y"], ann_dict["w"], ann_dict["h"],
                ann_dict.get("points"),
            )

    def _on_ann_selected(self, ann_id: int):
        self._canvas.set_selected(ann_id)

    def _assign_label(self):
        if self._pending_ann_id is None:
            return
        label = self._label_combo.currentText().strip()
        if label:
            self._state.assign_label(self._pending_ann_id, label)
        self._pending_ann_id = None
        self._label_panel.hide()
        self._load_current_image()

    def _cancel_pending(self):
        if self._pending_ann_id is not None:
            img = self._state.get_selected_image()
            if img:
                self._state.delete_annotation(self._pending_ann_id, img.id)
        self._pending_ann_id = None
        self._label_panel.hide()
        self._load_current_image()

    def _delete_ann(self, ann_id: int):
        img = self._state.get_selected_image()
        if img:
            self._state.delete_annotation(ann_id, img.id)
            self._load_current_image()

    def _pick_more(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Add Images", "", IMG_EXTS)
        if paths:
            self._state.add_images(paths)
            self._state.notify(f"{len(paths)} image(s) added.")
