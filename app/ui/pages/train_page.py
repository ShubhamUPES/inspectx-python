from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QProgressBar, QScrollArea,
)
from PyQt6.QtCore import Qt
from app.ui.theme import (
    WHITE, GRAY_50, GRAY_100, GRAY_200, GRAY_400, GRAY_500,
    GRAY_700, GRAY_900, VIOLET_50, VIOLET_200, VIOLET_600,
    EMERALD_50, EMERALD_200, EMERALD_600, EMERALD_700,
    AMBER_50, AMBER_200, AMBER_600,
    CONTENT_BG,
)
from app.ui.widgets.card import Card
from app.ui.widgets.metric_card import MetricCard


class TrainPage(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state = state
        self._training = False
        self._build()
        state.project_changed.connect(self.refresh)
        state.training_progress.connect(self._on_progress)
        state.training_finished.connect(self._on_finished)

    def _build(self):
        self.setStyleSheet(f"background:{CONTENT_BG};")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self._main_card = Card("Train Model", "Select Dataset Version → Configure → Train.", "green")
        self._output_card = Card("Training Output", "Completed training adds a model to Models.", "amber")
        self._output_card.setFixedWidth(300)

        root.addWidget(self._main_card, 1)
        root.addWidget(self._output_card)

        self._build_output_panel()
        self.refresh()

    def _build_output_panel(self):
        cl = self._output_card.content_layout()

        info = QLabel("Use dataset versions for reproducible training and rollback.")
        info.setStyleSheet(
            f"font-size:12px;color:{GRAY_500};background:transparent;border:none;"
        )
        info.setWordWrap(True)
        cl.addWidget(info)

        box = QWidget()
        box.setStyleSheet(f"""
            QWidget {{
                background:{GRAY_50};border:1px solid {GRAY_200};border-radius:10px;
            }}
        """)
        bl = QVBoxLayout(box)
        bl.setContentsMargins(12, 10, 12, 10)
        bl.setSpacing(4)
        t = QLabel("Training Configuration")
        t.setStyleSheet(
            f"font-size:12px;font-weight:700;color:{GRAY_900};background:transparent;border:none;"
        )
        self._config_lbl = QLabel("Select a version and parameters above.")
        self._config_lbl.setStyleSheet(
            f"font-size:11px;color:{GRAY_500};background:transparent;border:none;"
        )
        self._config_lbl.setWordWrap(True)
        bl.addWidget(t)
        bl.addWidget(self._config_lbl)
        cl.addWidget(box)

        log_lbl = QLabel("Training Logs")
        log_lbl.setStyleSheet(
            f"font-size:12px;font-weight:600;color:{GRAY_700};background:transparent;border:none;"
        )
        cl.addWidget(log_lbl)

        self._log_scroll = QScrollArea()
        self._log_scroll.setWidgetResizable(True)
        self._log_scroll.setStyleSheet("background:transparent;border:none;")
        self._log_widget = QWidget()
        self._log_widget.setStyleSheet("background:transparent;")
        self._log_layout = QVBoxLayout(self._log_widget)
        self._log_layout.setSpacing(4)
        self._log_layout.setContentsMargins(0, 0, 0, 0)
        self._log_scroll.setWidget(self._log_widget)
        cl.addWidget(self._log_scroll, 1)

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

    # ── refresh ────────────────────────────────────────────────────────────────

    def refresh(self):
        cl = self._main_card.content_layout()
        self._clear_cl(cl)

        p = self._state.project
        if not p:
            return

        version = self._state.active_version()

        # ── metrics strip (wrapped in QWidget) ──
        met_w, met_r = self._row_widget(spacing=8)
        for lbl, val, tone in [
            ("Dataset Version", version.name if version else "None",
             "green" if version else "amber"),
            ("Images", str(version.image_count if version else 0), "gray"),
            ("Type", "Detection" if p.type == "detection" else "Segmentation", "purple"),
            ("Models", str(len(p.ml_models)), "green"),
        ]:
            met_r.addWidget(MetricCard(lbl, val, tone))
        cl.addWidget(met_w)

        # ── version selector ──
        ver_lbl = QLabel("Select Dataset Version")
        ver_lbl.setStyleSheet(
            f"font-size:12px;font-weight:600;color:{GRAY_700};background:transparent;border:none;"
        )
        cl.addWidget(ver_lbl)

        self._version_combo = QComboBox()
        self._version_combo.setFixedHeight(38)
        self._version_combo.setStyleSheet(f"""
            QComboBox {{
                background:{GRAY_50};border:1px solid {GRAY_200};
                border-radius:9px;padding:0 10px;font-size:12px;color:{GRAY_700};
            }}
            QComboBox::drop-down {{ border:none;width:20px; }}
        """)
        if p.versions:
            for v in p.versions:
                self._version_combo.addItem(f"{v.name} · {v.image_count} images", v.id)
        else:
            self._version_combo.addItem("No dataset version — generate one first", -1)
        if version:
            idx = next(
                (i for i in range(self._version_combo.count())
                 if self._version_combo.itemData(i) == version.id),
                0,
            )
            self._version_combo.setCurrentIndex(idx)
        cl.addWidget(self._version_combo)

        # ── hyperparameters ──
        params_lbl = QLabel("Hyperparameters")
        params_lbl.setStyleSheet(
            f"font-size:12px;font-weight:600;color:{GRAY_700};background:transparent;border:none;"
        )
        cl.addWidget(params_lbl)

        params_w, params_r = self._row_widget(spacing=8)
        self._params: dict[str, QLineEdit] = {}
        for name, default in [
            ("Epochs", "100"),
            ("Batch Size", "16"),
            ("Image Size", "640"),
            ("Learning Rate", "0.001"),
        ]:
            box = QWidget()
            box.setStyleSheet(
                f"background:{GRAY_50};border:1px solid {GRAY_200};border-radius:9px;"
            )
            bl = QVBoxLayout(box)
            bl.setContentsMargins(10, 8, 10, 8)
            bl.setSpacing(4)
            lbl = QLabel(name)
            lbl.setStyleSheet(
                f"font-size:10px;color:{GRAY_500};background:transparent;border:none;"
            )
            inp = QLineEdit(default)
            inp.setStyleSheet(f"""
                QLineEdit {{
                    background:{WHITE};border:1px solid {GRAY_200};
                    border-radius:7px;padding:4px 8px;font-size:12px;color:{GRAY_900};
                }}
                QLineEdit:focus {{ border-color:{VIOLET_600}; }}
            """)
            inp.setFixedHeight(30)
            bl.addWidget(lbl)
            bl.addWidget(inp)
            self._params[name] = inp
            params_r.addWidget(box)
        cl.addWidget(params_w)

        # ── split mode ──
        split_w, split_r = self._row_widget(spacing=8)
        for lbl_text, items, default in [
            ("Split Mode",  ["Auto Split", "Manual Split"], "Auto Split"),
            ("Split Ratio", ["80 / 15 / 5", "70 / 20 / 10"], "80 / 15 / 5"),
        ]:
            box = QWidget()
            box.setStyleSheet(
                f"background:{GRAY_50};border:1px solid {GRAY_200};border-radius:9px;"
            )
            bl = QVBoxLayout(box)
            bl.setContentsMargins(10, 8, 10, 8)
            bl.setSpacing(4)
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet(
                f"font-size:10px;color:{GRAY_500};background:transparent;border:none;"
            )
            c = QComboBox()
            c.addItems(items)
            c.setStyleSheet(f"""
                QComboBox {{
                    background:{WHITE};border:1px solid {GRAY_200};
                    border-radius:7px;padding:0 8px;font-size:12px;color:{GRAY_900};
                }}
                QComboBox::drop-down {{ border:none;width:20px; }}
            """)
            c.setFixedHeight(30)
            bl.addWidget(lbl)
            bl.addWidget(c)
            split_r.addWidget(box)
        split_r.addStretch()
        cl.addWidget(split_w)

        # ── train button ──
        self._train_btn = QPushButton("⚡  Train Model")
        self._train_btn.setFixedHeight(44)
        self._train_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._train_btn.setEnabled(bool(p.versions) and not self._training)
        self._train_btn.setStyleSheet(f"""
            QPushButton {{
                background:{EMERALD_600};color:white;
                border:none;border-radius:11px;
                font-size:13px;font-weight:700;
            }}
            QPushButton:hover {{ background:{EMERALD_700}; }}
            QPushButton:disabled {{
                background:{GRAY_100};color:{GRAY_400};
            }}
        """)
        self._train_btn.clicked.connect(self._start_training)
        cl.addWidget(self._train_btn)

        # ── progress ──
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setFixedHeight(10)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background:{GRAY_200};border:none;border-radius:5px;
            }}
            QProgressBar::chunk {{
                background:{EMERALD_600};border-radius:5px;
            }}
        """)
        self._progress_bar.hide()
        cl.addWidget(self._progress_bar)

        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(
            f"font-size:11px;color:{GRAY_500};background:transparent;border:none;"
        )
        self._progress_lbl.hide()
        cl.addWidget(self._progress_lbl)

        # ── result metrics (hidden until training completes) ──
        self._metrics_widget = QWidget()
        self._metrics_widget.setStyleSheet("background:transparent;border:none;")
        mr = QHBoxLayout(self._metrics_widget)
        mr.setContentsMargins(0, 0, 0, 0)
        mr.setSpacing(8)
        for ml, mv, tn in [
            ("Loss", "—", "amber"),
            ("mAP@50", "—", "green"),
            ("Precision", "—", "gray"),
            ("Recall", "—", "purple"),
        ]:
            mr.addWidget(MetricCard(ml, mv, tn))
        self._metrics_widget.hide()
        cl.addWidget(self._metrics_widget)
        cl.addStretch()

        self._update_logs(p)
        self._update_config()

    def _update_logs(self, p):
        while self._log_layout.count():
            item = self._log_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for log in [l for l in p.logs if l.log_type in ("Model", "Version")][:10]:
            row = QWidget()
            row.setStyleSheet(
                f"background:{GRAY_50};border:1px solid {GRAY_200};border-radius:8px;"
            )
            rl = QHBoxLayout(row)
            rl.setContentsMargins(8, 6, 8, 6)
            rl.setSpacing(8)
            t = QLabel(log.time_str)
            t.setStyleSheet(
                f"font-size:10px;font-weight:600;color:{GRAY_700};background:transparent;border:none;"
            )
            m = QLabel(log.message)
            m.setStyleSheet(
                f"font-size:10px;color:{GRAY_500};background:transparent;border:none;"
            )
            m.setWordWrap(True)
            rl.addWidget(t)
            rl.addWidget(m, 1)
            self._log_layout.addWidget(row)
        self._log_layout.addStretch()

    def _update_config(self):
        p = self._state.project
        version = self._state.active_version()
        if p and version:
            self._config_lbl.setText(
                f"Dataset: {version.name} · Split: 80/15/5 · "
                f"Epochs: 100 · Images: {version.image_count}"
            )

    def _start_training(self):
        version = self._state.active_version()
        if not version:
            self._state.notify("Generate a dataset version first.")
            return
        self._training = True
        self._train_btn.setEnabled(False)
        self._train_btn.setText("Training…")
        self._progress_bar.setValue(0)
        self._progress_bar.show()
        self._progress_lbl.show()
        self._metrics_widget.show()
        self._state.start_training(version.id, version.name)

    def _on_progress(self, value: int):
        self._progress_bar.setValue(value)
        self._progress_lbl.setText(f"Epoch progress: {value}%")

    def _on_finished(self):
        self._training = False
        self._train_btn.setEnabled(True)
        self._train_btn.setText("⚡  Train Model")
        self._progress_bar.setValue(100)
        self._progress_lbl.setText("Training complete!")
        p = self._state.project
        if p:
            self._update_logs(p)
