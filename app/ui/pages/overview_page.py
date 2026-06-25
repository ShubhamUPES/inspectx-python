"""
OverviewPage — project dashboard shown immediately after opening a project.
"""
from __future__ import annotations
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.ui.theme import (
    WHITE, GRAY_50, GRAY_100, GRAY_200, GRAY_400, GRAY_500,
    GRAY_700, GRAY_900, VIOLET_50, VIOLET_200, VIOLET_500, VIOLET_600,
    EMERALD_50, EMERALD_200, EMERALD_600,
    AMBER_50, AMBER_200, AMBER_600,
    RED_50, RED_200, RED_600,
    CONTENT_BG,
)
from app.ui.widgets.card import Card
from app.ui.widgets.metric_card import MetricCard
from app.ui.widgets.badge import Badge


class OverviewPage(QWidget):
    navigate = pyqtSignal(str)

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self._state = state
        self._build()
        state.project_changed.connect(self.refresh)

    def _build(self):
        self.setStyleSheet(f"background:{CONTENT_BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        self._card = Card("Project Overview", "Pipeline status and quick actions.", "purple")
        root.addWidget(self._card)
        self.refresh()

    def refresh(self):
        cl = self._card.content_layout()
        while cl.count():
            item = cl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        p = self._state.project
        if not p:
            empty = QLabel("No project open.")
            empty.setStyleSheet(f"font-size:12px;color:{GRAY_400};background:transparent;border:none;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(empty, 1)
            return

        # ── Top metrics ──────────────────────────────────────────────────────
        metrics_w = QWidget()
        metrics_w.setStyleSheet("background:transparent;border:none;")
        mr = QHBoxLayout(metrics_w)
        mr.setContentsMargins(0, 0, 0, 0)
        mr.setSpacing(8)
        annotated = p.annotated_count()
        total     = len(p.images)
        version   = self._state.active_version()
        model     = self._state.active_model()
        for lbl, val, tone in [
            ("Total Images",    str(total),                    "gray"),
            ("Annotated",       f"{annotated}/{total}",        "green"),
            ("Dataset Version", version.name if version else "—", "purple" if version else "amber"),
            ("Active Model",    model.name  if model  else "—",   "green"  if model  else "amber"),
        ]:
            mr.addWidget(MetricCard(lbl, val, tone))
        cl.addWidget(metrics_w)

        # ── Pipeline progress bar ─────────────────────────────────────────────
        pipeline_w = QWidget()
        pipeline_w.setStyleSheet(f"background:{WHITE};border:1px solid {GRAY_200};border-radius:14px;")
        pl = QVBoxLayout(pipeline_w)
        pl.setContentsMargins(16, 12, 16, 12)
        pl.setSpacing(8)
        ph = QLabel("Pipeline Progress")
        ph.setStyleSheet(f"font-size:12px;font-weight:700;color:{GRAY_900};background:transparent;border:none;")
        pl.addWidget(ph)

        steps = [
            ("Upload Data",      total > 0,      "upload"),
            ("Annotate",         annotated > 0,  "annotate"),
            ("Generate Version", version is not None, "versions"),
            ("Train Model",      model is not None,   "train"),
            ("Test & Deploy",    model is not None and model.deployment == "Production", "test"),
        ]
        steps_row = QHBoxLayout()
        steps_row.setSpacing(0)
        for i, (label, done, route) in enumerate(steps):
            step_w = QWidget()
            step_w.setStyleSheet("background:transparent;border:none;")
            swl = QVBoxLayout(step_w)
            swl.setContentsMargins(0, 0, 0, 0)
            swl.setSpacing(4)
            swl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            circle = QLabel("✓" if done else str(i + 1))
            circle.setFixedSize(32, 32)
            circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if done:
                circle.setStyleSheet(f"background:{EMERALD_600};color:white;border-radius:16px;font-weight:700;font-size:13px;")
            else:
                circle.setStyleSheet(f"background:{GRAY_100};color:{GRAY_400};border:2px solid {GRAY_200};border-radius:16px;font-size:12px;font-weight:600;")

            lbl_w = QLabel(label)
            lbl_w.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            lbl_w.setStyleSheet(f"font-size:10px;font-weight:600;color:{EMERALD_600 if done else GRAY_400};background:transparent;border:none;")
            lbl_w.setWordWrap(True)
            lbl_w.setFixedWidth(70)
            swl.addWidget(circle, 0, Qt.AlignmentFlag.AlignHCenter)
            swl.addWidget(lbl_w, 0, Qt.AlignmentFlag.AlignHCenter)
            r = route
            step_w.setCursor(Qt.CursorShape.PointingHandCursor)
            step_w.mousePressEvent = lambda e, r=r: self.navigate.emit(r)
            steps_row.addWidget(step_w, 1)

            if i < len(steps) - 1:
                line = QWidget()
                line.setFixedHeight(2)
                line.setFixedWidth(20)
                line.setStyleSheet(f"background:{EMERALD_200 if done else GRAY_200};border:none;")
                steps_row.addWidget(line, 0, Qt.AlignmentFlag.AlignVCenter)

        pl.addLayout(steps_row)
        cl.addWidget(pipeline_w)

        # ── Quick actions ─────────────────────────────────────────────────────
        quick_w = QWidget()
        quick_w.setStyleSheet("background:transparent;border:none;")
        ql = QHBoxLayout(quick_w)
        ql.setContentsMargins(0, 0, 0, 0)
        ql.setSpacing(8)

        actions = [
            ("⬆  Upload Images",    "upload",    "purple"),
            ("✎  Annotate",          "annotate",  "purple"),
            ("⊞  New Version",       "versions",  "green"),
            ("⚡  Train Model",      "train",     "green"),
            ("▶  Test Model",        "test",      "amber"),
        ]
        for label, route, tone in actions:
            btn = QPushButton(label)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            r = route
            btn.clicked.connect(lambda checked, r=r: self.navigate.emit(r))
            colors = {
                "purple": (VIOLET_50, VIOLET_200, VIOLET_600),
                "green":  (EMERALD_50, EMERALD_200, EMERALD_600),
                "amber":  (AMBER_50, AMBER_200, AMBER_600),
            }
            bg, border, fg = colors[tone]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:{bg};color:{fg};
                    border:1px solid {border};border-radius:9px;
                    padding:0 14px;font-size:11px;font-weight:600;
                }}
                QPushButton:hover {{ opacity:0.85; }}
            """)
            ql.addWidget(btn)
        ql.addStretch()
        cl.addWidget(quick_w)

        # ── Recent logs ───────────────────────────────────────────────────────
        log_hdr = QLabel("Recent Activity")
        log_hdr.setStyleSheet(f"font-size:12px;font-weight:700;color:{GRAY_900};background:transparent;border:none;")
        cl.addWidget(log_hdr)

        log_scroll = QScrollArea()
        log_scroll.setWidgetResizable(True)
        log_scroll.setFixedHeight(140)
        log_scroll.setStyleSheet("background:transparent;border:none;")
        log_w = QWidget()
        log_w.setStyleSheet("background:transparent;")
        ll = QVBoxLayout(log_w)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(4)

        logs = p.logs[:8] if p.logs else []
        if logs:
            for log in logs:
                row = QWidget()
                row.setStyleSheet(f"background:{GRAY_50};border:1px solid {GRAY_200};border-radius:7px;")
                rl = QHBoxLayout(row)
                rl.setContentsMargins(10, 5, 10, 5)
                rl.setSpacing(8)
                t = QLabel(log.time_str)
                t.setStyleSheet(f"font-size:10px;font-weight:600;color:{GRAY_700};background:transparent;border:none;")
                t.setFixedWidth(60)
                badge_tone = {"System":"gray","Version":"purple","Model":"green"}.get(log.log_type,"gray")
                b = Badge(log.log_type, badge_tone)
                m = QLabel(log.message)
                m.setStyleSheet(f"font-size:10px;color:{GRAY_500};background:transparent;border:none;")
                m.setWordWrap(True)
                rl.addWidget(t)
                rl.addWidget(b)
                rl.addWidget(m, 1)
                ll.addWidget(row)
        else:
            empty = QLabel("No activity yet.")
            empty.setStyleSheet(f"font-size:11px;color:{GRAY_400};background:transparent;border:none;")
            ll.addWidget(empty)
        ll.addStretch()
        log_scroll.setWidget(log_w)
        cl.addWidget(log_scroll)
        cl.addStretch()
