from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QPainter
from app.ui.theme import (
    WHITE, GRAY_50, GRAY_100, GRAY_200, GRAY_300, GRAY_400, GRAY_500, GRAY_700, GRAY_900,
    VIOLET_50, VIOLET_200, VIOLET_600,
    EMERALD_50, EMERALD_200, EMERALD_600, EMERALD_700,
    RED_50, RED_200, RED_400, RED_600,
    AMBER_50, AMBER_200, AMBER_600,
    CONTENT_BG,
)
from app.ui.widgets.card import Card
from app.ui.widgets.metric_card import MetricCard

IMG_EXTS = "Images (*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp)"


def _placeholder_pixmap(w: int, h: int, text: str = "") -> QPixmap:
    px = QPixmap(w, h)
    px.fill(QColor("#F1F5F9"))
    painter = QPainter(px)
    painter.setPen(QColor(GRAY_300))
    margin = 2
    painter.drawRoundedRect(margin, margin, w - margin * 2 - 1, h - margin * 2 - 1, 8, 8)
    if text:
        painter.setPen(QColor(GRAY_400))
        painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, text)
    painter.end()
    return px


class TestPage(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state = state
        self._result = None
        self._test_image_path = ""
        self._build()
        state.project_changed.connect(self._on_project_changed)

    def _build(self):
        self.setStyleSheet(f"background:{CONTENT_BG};")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self._main_card = Card("Model Test", "Upload a test image and run inference.", "purple")
        self._result_card = Card("Predictions", "Inference results will appear here.", "amber")
        self._result_card.setFixedWidth(280)

        root.addWidget(self._main_card, 1)
        root.addWidget(self._result_card)

        self._build_result_panel()
        self.refresh()

    def _build_result_panel(self):
        cl = self._result_card.content_layout()
        cl.setSpacing(8)
        self._result_metrics: list[MetricCard] = []
        for lbl, val, tone in [
            ("Prediction",      "Not Run", "gray"),
            ("Confidence",      "—",       "gray"),
            ("Inference Time",  "—",       "amber"),
            ("Objects Detected","—",       "gray"),
        ]:
            m = MetricCard(lbl, val, tone)
            cl.addWidget(m)
            self._result_metrics.append(m)
        cl.addStretch()

    # ── helpers ────────────────────────────────────────────────────────────────

    def _row_widget(self, spacing: int = 8) -> tuple[QWidget, QHBoxLayout]:
        w = QWidget()
        w.setStyleSheet("background:transparent;border:none;")
        rl = QHBoxLayout(w)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(spacing)
        return w, rl

    def _clear_cl(self, cl):
        while cl.count():
            item = cl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_project_changed(self):
        self._test_image_path = ""
        self._result = None
        self.refresh()

    # ── refresh ────────────────────────────────────────────────────────────────

    def refresh(self):
        cl = self._main_card.content_layout()
        self._clear_cl(cl)

        p = self._state.project
        if not p:
            return

        model = self._state.active_model()

        # ── action buttons ──
        btn_w, btn_r = self._row_widget(spacing=8)
        up_btn = QPushButton("⬆  Upload Test Image")
        up_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        up_btn.setStyleSheet(f"""
            QPushButton {{
                background:{VIOLET_50};color:{VIOLET_600};
                border:1px solid {VIOLET_200};border-radius:9px;
                padding:7px 14px;font-size:12px;font-weight:600;
            }}
            QPushButton:hover {{ background:{VIOLET_200}; }}
        """)
        up_btn.clicked.connect(self._upload_test_image)

        run_btn = QPushButton("▶  Run Inference")
        run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        run_btn.setEnabled(bool(model) and bool(self._test_image_path))
        run_btn.setStyleSheet(f"""
            QPushButton {{
                background:{EMERALD_600};color:white;
                border:none;border-radius:9px;
                padding:7px 14px;font-size:12px;font-weight:700;
            }}
            QPushButton:hover {{ background:{EMERALD_700}; }}
            QPushButton:disabled {{
                background:{GRAY_100};color:{GRAY_400};
            }}
        """)
        run_btn.clicked.connect(self._run_test)
        btn_r.addWidget(up_btn)
        btn_r.addWidget(run_btn)
        btn_r.addStretch()
        cl.addWidget(btn_w)

        # ── status strip ──
        info_w, info_r = self._row_widget(spacing=8)
        img_name = self._test_image_path.split("/")[-1] if self._test_image_path else "No image"
        for lbl, val, tone in [
            ("Active Model", model.name if model else "No model",
             "green" if model else "amber"),
            ("Test Image",   img_name, "purple" if self._test_image_path else "gray"),
            ("Status", "Ready" if (model and self._test_image_path) else
             ("No model" if not model else "Upload image"), "green" if model else "red"),
        ]:
            info_r.addWidget(MetricCard(lbl, val, tone))
        info_r.addStretch()
        cl.addWidget(info_w)

        # ── image preview / canvas ──
        if self._test_image_path:
            from pathlib import Path
            preview = QLabel()
            preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview.setStyleSheet(
                f"background:{GRAY_50};border:1px solid {GRAY_200};"
                f"border-radius:12px;border:none;"
            )
            preview.setMinimumHeight(280)
            if Path(self._test_image_path).exists():
                px = QPixmap(self._test_image_path).scaled(
                    600, 380,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                preview.setPixmap(px)
            cl.addWidget(preview, 1)
        else:
            placeholder = QLabel()
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setMinimumHeight(280)
            placeholder.setPixmap(_placeholder_pixmap(600, 280, "Upload a test image to begin"))
            placeholder.setStyleSheet(
                f"background:{GRAY_50};border:2px dashed {GRAY_200};"
                f"border-radius:12px;"
            )
            cl.addWidget(placeholder, 1)

        # ── result overlay (shown after inference) ──
        if self._result:
            res_w, res_r = self._row_widget(spacing=8)
            decision = self._result.get("decision", "—")
            tone_d = "red" if decision == "FAIL" else "green"
            for ml, mv, tn in [
                ("Decision",   decision,                              tone_d),
                ("Confidence", self._result.get("confidence", "—"),  "gray"),
                ("Inference",  self._result.get("inference",  "—"),  "amber"),
                ("Objects",    self._result.get("objects",    "—"),  "purple"),
            ]:
                res_r.addWidget(MetricCard(ml, mv, tn))
            cl.addWidget(res_w)

            # Update side panel metrics
            vals = [
                (decision, tone_d),
                (self._result.get("confidence", "—"), "gray"),
                (self._result.get("inference",   "—"), "amber"),
                (self._result.get("objects",     "—"), "gray"),
            ]
            labels = ["Prediction", "Confidence", "Inference Time", "Objects Detected"]
            for i, m in enumerate(self._result_metrics):
                v, t = vals[i]
                m._tone = t
                m.update_value(labels[i], v)

    def _upload_test_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Test Image", "", IMG_EXTS)
        if path:
            self._test_image_path = path
            self._result = None
            self._state.notify("Test image loaded.")
            self.refresh()

    def _run_test(self):
        p = self._state.project
        if not p:
            return
        model = self._state.active_model()
        if not model:
            self._state.notify("Train and promote a model first.")
            return
        if not self._test_image_path:
            self._state.notify("Upload a test image first.")
            return
        self._result = self._state.run_inspection()
        self.refresh()
        decision = self._result.get("decision", "?")
        self._state.notify(f"Inference complete: {decision}")
