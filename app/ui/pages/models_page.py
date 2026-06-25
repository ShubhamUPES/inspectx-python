from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen
from app.ui.theme import (
    WHITE, GRAY_50, GRAY_100, GRAY_200, GRAY_400, GRAY_500,
    GRAY_700, GRAY_900, VIOLET_50, VIOLET_200, VIOLET_500, VIOLET_600,
    EMERALD_50, EMERALD_200, EMERALD_600,
    AMBER_50, AMBER_200, AMBER_600,
    CONTENT_BG,
)
from app.ui.widgets.card import Card
from app.ui.widgets.metric_card import MetricCard
from app.ui.widgets.badge import Badge


class MiniChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self._values = [42, 58, 51, 72, 66, 81, 75, 92, 88, 95]

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(WHITE))
        p.setPen(QPen(QColor(GRAY_200), 1))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        bar_w = (self.width() - 8) / max(len(self._values), 1)
        for i, v in enumerate(self._values):
            h = int(v / 100 * (self.height() - 8))
            x = 4 + i * bar_w
            y = self.height() - 4 - h
            p.fillRect(int(x) + 1, int(y), int(bar_w) - 2, h, QColor("#A78BFA"))
        p.end()


class ModelsPage(QWidget):
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
        self._card = Card("Models", "Compare metrics, retrain, and test trained models.", "green")
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
            return

        if not p.ml_models:
            empty = QWidget()
            el = QVBoxLayout(empty)
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            e1 = QLabel("No trained models yet.")
            e1.setStyleSheet(f"font-size:13px;color:{GRAY_500};background:transparent;border:none;")
            e1.setAlignment(Qt.AlignmentFlag.AlignCenter)
            e2 = QLabel("Generate a dataset version, then train a model.")
            e2.setStyleSheet(f"font-size:11px;color:{GRAY_400};background:transparent;border:none;")
            e2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            go = QPushButton("Go to Train")
            go.setFixedWidth(140)
            go.setCursor(Qt.CursorShape.PointingHandCursor)
            go.setStyleSheet(f"""
                QPushButton {{
                    background:{VIOLET_600};color:white;border:none;
                    border-radius:9px;padding:8px;font-size:12px;font-weight:600;
                }}
                QPushButton:hover {{ background:{VIOLET_500}; }}
            """)
            go.clicked.connect(lambda: self.navigate.emit("train"))
            el.addWidget(e1)
            el.addWidget(e2)
            el.addSpacing(8)
            el.addWidget(go, 0, Qt.AlignmentFlag.AlignHCenter)
            cl.addWidget(empty, 1)
            return

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent;border:none;")
        grid_w = QWidget()
        grid_w.setStyleSheet("background:transparent;")
        gl = QGridLayout(grid_w)
        gl.setSpacing(12)
        gl.setContentsMargins(0, 0, 0, 0)

        cols = 2
        for i, model in enumerate(p.ml_models):
            row, col = divmod(i, cols)
            mc = self._model_card(model)
            gl.addWidget(mc, row, col)

        scroll.setWidget(grid_w)
        cl.addWidget(scroll, 1)

    def _model_card(self, model) -> QWidget:
        card = QWidget()
        card.setStyleSheet(f"background:{GRAY_50};border:1px solid {GRAY_200};border-radius:14px;")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 12, 14, 12)
        cl.setSpacing(8)

        hdr = QHBoxLayout()
        name_col = QVBoxLayout()
        name_col.setSpacing(2)
        nlbl = QLabel(model.name)
        nlbl.setStyleSheet(f"font-size:13px;font-weight:700;color:{GRAY_900};background:transparent;border:none;")
        dlbl = QLabel(f"{model.version_label} · {model.dataset_version}")
        dlbl.setStyleSheet(f"font-size:10px;color:{GRAY_500};background:transparent;border:none;")
        name_col.addWidget(nlbl)
        name_col.addWidget(dlbl)
        hdr.addLayout(name_col, 1)
        hdr.addWidget(Badge("Production" if model.deployment == "Production" else "Registry",
                            "green" if model.deployment == "Production" else "gray"))
        cl.addLayout(hdr)

        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(6)
        for ml, mv, tone in [
            ("mAP", model.map_score, "green"),
            ("Precision", model.precision, "gray"),
            ("Recall", model.recall, "purple"),
            ("Latency", model.latency, "amber"),
        ]:
            metrics_row.addWidget(MetricCard(ml, mv, tone))
        cl.addLayout(metrics_row)

        cl.addWidget(MiniChart())

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        for blbl, tone, callback in [
            ("Promote to Production", "green", lambda mid=model.id: self._promote(mid)),
            ("Test", "purple", lambda: self.navigate.emit("test")),
            ("Delete", "red", lambda mid=model.id: self._delete(mid)),
        ]:
            b = QPushButton(blbl)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            colors = {
                "green":  (EMERALD_50, EMERALD_200, EMERALD_600),
                "purple": (VIOLET_50, VIOLET_200, VIOLET_600),
                "red":    ("#FEF2F2", "#FECACA", "#DC2626"),
            }
            bg, border, fg = colors[tone]
            b.setStyleSheet(f"""
                QPushButton {{
                    background:{bg};color:{fg};
                    border:1px solid {border};border-radius:8px;
                    padding:5px 10px;font-size:11px;font-weight:600;
                }}
                QPushButton:hover {{ opacity:0.85; }}
            """)
            b.clicked.connect(callback)
            btn_row.addWidget(b)
        btn_row.addStretch()
        cl.addLayout(btn_row)
        return card

    def _promote(self, model_id: int):
        self._state.promote_model(model_id)

    def _delete(self, model_id: int):
        self._state.delete_model(model_id)
