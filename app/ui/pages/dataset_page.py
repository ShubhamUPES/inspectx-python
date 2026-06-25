from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QLineEdit, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.ui.theme import (
    WHITE, GRAY_50, GRAY_200, GRAY_400, GRAY_500,
    GRAY_700, GRAY_900, VIOLET_50, VIOLET_200, VIOLET_600,
    EMERALD_50, EMERALD_200, EMERALD_600, EMERALD_700,
    AMBER_50, AMBER_200, AMBER_600,
    RED_50, RED_200, RED_400, RED_600,
    CONTENT_BG,
)
from app.ui.widgets.card import Card
from app.ui.widgets.metric_card import MetricCard
from app.ui.widgets.image_card import ImageCard


class DatasetPage(QWidget):
    navigate = pyqtSignal(str)

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state = state
        self._filter = "All Images"
        self._search = ""
        self._selected_ids: list[int] = []
        self._build()
        state.project_changed.connect(self.refresh)

    def _build(self):
        self.setStyleSheet(f"background:{CONTENT_BG};")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self._main_card = Card("Dataset", "Working image set and annotation status.", "green")
        self._sidebar_card = Card("Dataset Lifecycle", "Versions and retraining workflow.", "amber")
        self._sidebar_card.setFixedWidth(260)

        root.addWidget(self._main_card, 1)
        root.addWidget(self._sidebar_card)

        self.refresh()

    def refresh(self):
        self._rebuild_main()
        self._rebuild_sidebar()

    # ── helpers ────────────────────────────────────────────────────────────────

    def _row_widget(self, spacing: int = 8, stretch: bool = False) -> tuple[QWidget, QHBoxLayout]:
        """Return a (container QWidget, QHBoxLayout) pair so rows are proper widgets."""
        w = QWidget()
        w.setStyleSheet("background:transparent;border:none;")
        rl = QHBoxLayout(w)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(spacing)
        if stretch:
            rl.addStretch()
        return w, rl

    def _clear_cl(self, cl):
        while cl.count():
            item = cl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ── main card ──────────────────────────────────────────────────────────────

    def _rebuild_main(self):
        cl = self._main_card.content_layout()
        self._clear_cl(cl)

        p = self._state.project
        if not p:
            return

        # ── search + split metrics ──
        top_w, top_r = self._row_widget(spacing=8)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search images, classes, tags…")
        self._search_input.setFixedHeight(34)
        self._search_input.setText(self._search)
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background:{GRAY_50};border:1px solid {GRAY_200};
                border-radius:9px;padding:0 10px;font-size:12px;color:{GRAY_900};
            }}
            QLineEdit:focus {{ border-color:{VIOLET_600}; }}
        """)
        self._search_input.textChanged.connect(self._on_search)
        top_r.addWidget(self._search_input, 2)
        for split, count, tone in [
            ("Train", sum(1 for i in p.images if i.split == "Train"), "green"),
            ("Valid", sum(1 for i in p.images if i.split == "Valid"), "amber"),
            ("Test",  sum(1 for i in p.images if i.split == "Test"),  "purple"),
        ]:
            top_r.addWidget(MetricCard(split, str(count), tone))
        cl.addWidget(top_w)

        # ── filter tabs ──
        tab_w, tab_r = self._row_widget(spacing=6)
        for flt in ["All Images", "Annotated", "Unannotated"]:
            btn = QPushButton(flt)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            active = (flt == self._filter)
            if active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background:{EMERALD_600};color:white;
                        border:none;border-radius:8px;
                        padding:5px 14px;font-size:11px;font-weight:600;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background:{WHITE};color:{GRAY_700};
                        border:1px solid {GRAY_200};border-radius:8px;
                        padding:5px 14px;font-size:11px;font-weight:600;
                    }}
                    QPushButton:hover {{ background:{GRAY_50}; }}
                """)
            f = flt
            btn.clicked.connect(lambda checked, flt=f: self._set_filter(flt))
            tab_r.addWidget(btn)
        tab_r.addStretch()
        cl.addWidget(tab_w)

        # ── action bar ──
        all_visible = self._get_visible(p)
        all_sel = len(all_visible) > 0 and all(img.id in self._selected_ids for img in all_visible)

        act_w, act_r = self._row_widget(spacing=6)
        for lbl, style, callback, disabled in [
            ("+ Add Images", "ghost",   lambda: self.navigate.emit("upload"), False),
            ("Train",        "green",   lambda: self.navigate.emit("train"),  False),
            ("Select All" if not all_sel else "Deselect All", "ghost",
             self._toggle_select_all, len(all_visible) == 0),
            ("Re-Annotate",  "purple",  self._reannotate,      len(self._selected_ids) == 0),
            ("Delete",       "red",     self._delete_selected, len(self._selected_ids) == 0),
        ]:
            btn = self._action_btn(lbl, style, disabled)
            btn.clicked.connect(callback)
            act_r.addWidget(btn)
        act_r.addStretch()
        cl.addWidget(act_w)

        # ── image grid ──
        visible_imgs = self._get_visible(p)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent;border:none;")
        grid_w = QWidget()
        grid_w.setStyleSheet("background:transparent;")
        gl = QGridLayout(grid_w)
        gl.setSpacing(8)
        gl.setContentsMargins(0, 0, 0, 0)
        cols = 5
        for i, img in enumerate(visible_imgs):
            row, col = divmod(i, cols)
            card = ImageCard(img.id, img.name, img.file_path, img.status)
            card.set_selected(img.id in self._selected_ids)
            card.clicked.connect(self._state.select_image)
            card.toggled.connect(self._on_image_toggle)
            gl.addWidget(card, row, col)
        if not visible_imgs:
            empty = QLabel("No images in this view.\nTry another filter or add more images.")
            empty.setStyleSheet(
                f"font-size:12px;color:{GRAY_400};background:transparent;border:none;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            gl.addWidget(empty, 0, 0)
        scroll.setWidget(grid_w)
        cl.addWidget(scroll, 1)

    # ── sidebar card ───────────────────────────────────────────────────────────

    def _rebuild_sidebar(self):
        cl = self._sidebar_card.content_layout()
        self._clear_cl(cl)

        p = self._state.project
        if not p:
            return
        version = self._state.active_version()

        for lbl, val, tone in [
            ("Total Images",   str(len(p.images)),    "gray"),
            ("Active Version", version.name if version else "Working",
             "green" if version else "amber"),
            ("Versions",       str(len(p.versions)),  "green"),
            ("NG Captures",    str(len(p.failed_samples)), "red"),
        ]:
            cl.addWidget(MetricCard(lbl, val, tone))

        cl.addSpacing(4)

        for lbl, route, tone in [
            ("New Version",   "versions", "green"),
            ("Retrain Model", "train",    "purple"),
            ("Models",        "models",   "gray"),
        ]:
            btn = QPushButton(lbl)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            r = route
            btn.clicked.connect(lambda checked, r=r: self.navigate.emit(r))
            colors = {
                "green":  (EMERALD_50, EMERALD_600, EMERALD_700),
                "purple": (VIOLET_50, VIOLET_600, "#6D28D9"),
                "gray":   (GRAY_50, GRAY_700, GRAY_900),
            }
            bg, fg, hover_fg = colors[tone]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:{bg};color:{fg};
                    border:1px solid {GRAY_200};border-radius:9px;
                    padding:9px;font-size:12px;font-weight:600;
                    text-align:left;padding-left:14px;
                }}
                QPushButton:hover {{ color:{hover_fg};border-color:{fg}; }}
            """)
            cl.addWidget(btn)
        cl.addStretch()

    # ── logic helpers ──────────────────────────────────────────────────────────

    def _get_visible(self, p) -> list:
        imgs = p.images
        if self._filter == "Annotated":
            imgs = [i for i in imgs if i.status == "Annotated"]
        elif self._filter == "Unannotated":
            imgs = [i for i in imgs if i.status == "Unannotated"]
        if self._search:
            q = self._search.lower()
            imgs = [i for i in imgs if q in i.name.lower()
                    or any(q in lbl.lower() for lbl in i.labels)
                    or any(q in t.lower() for t in i.tags)]
        return imgs

    def _on_search(self, text: str):
        self._search = text
        self._rebuild_main()

    def _set_filter(self, f: str):
        self._filter = f
        self._rebuild_main()

    def _on_image_toggle(self, image_id: int, selected: bool):
        if selected and image_id not in self._selected_ids:
            self._selected_ids.append(image_id)
        elif not selected and image_id in self._selected_ids:
            self._selected_ids.remove(image_id)

    def _toggle_select_all(self):
        p = self._state.project
        if not p:
            return
        visible = self._get_visible(p)
        all_sel = all(img.id in self._selected_ids for img in visible)
        if all_sel:
            self._selected_ids = []
        else:
            self._selected_ids = [img.id for img in visible]
        self._rebuild_main()

    def _reannotate(self):
        if self._selected_ids:
            self._state.select_image(self._selected_ids[0])
            self.navigate.emit("annotate")

    def _delete_selected(self):
        if self._selected_ids:
            self._state.delete_images(list(self._selected_ids))
            self._selected_ids = []

    def _action_btn(self, label: str, tone: str, disabled: bool) -> QPushButton:
        btn = QPushButton(label)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setEnabled(not disabled)
        colors = {
            "ghost":  (WHITE,       GRAY_200,   GRAY_700,    GRAY_50),
            "green":  (EMERALD_50,  EMERALD_200, EMERALD_600, "#D1FAE5"),
            "purple": (VIOLET_50,   VIOLET_200,  VIOLET_600,  "#EDE9FE"),
            "red":    (RED_50,      RED_200,     RED_600,     "#FEE2E2"),
        }
        bg, border, fg, hover = colors.get(tone, colors["ghost"])
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{bg};border:1px solid {border};color:{fg};
                border-radius:8px;padding:5px 12px;font-size:11px;font-weight:600;
            }}
            QPushButton:hover {{ background:{hover}; }}
            QPushButton:disabled {{ color:{GRAY_400};border-color:{GRAY_200}; }}
        """)
        return btn
