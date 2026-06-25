from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from app.ui.theme import (
    WHITE, GRAY_50, GRAY_100, GRAY_200, GRAY_400, GRAY_500,
    GRAY_700, GRAY_900, VIOLET_50, VIOLET_200, VIOLET_500, VIOLET_600,
    EMERALD_50, EMERALD_200, EMERALD_600, RED_50, RED_200, RED_600,
    CONTENT_BG,
)
from app.ui.widgets.card import Card

CLASS_COLORS = ["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EF4444", "#06B6D4"]


class ClassesPage(QWidget):
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

        self._list_card = Card("Classes & Tags", "All defect classes used in annotations.", "purple")
        self._edit_card = Card("Bulk Edit", "Rename, merge, delete, and manage classes.", "green")

        root.addWidget(self._list_card, 1)
        root.addWidget(self._edit_card, 1)

        self._build_edit_card()
        self.refresh()

    def _build_edit_card(self):
        cl = self._edit_card.content_layout()
        cl.setSpacing(10)

        # Add class
        add_lbl = QLabel("Add New Class")
        add_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{GRAY_700};background:transparent;border:none;")
        cl.addWidget(add_lbl)

        add_row = QHBoxLayout()
        self._add_input = QLineEdit()
        self._add_input.setPlaceholderText("New class name…")
        self._add_input.setFixedHeight(36)
        self._add_input.setStyleSheet(f"""
            QLineEdit {{
                background:{GRAY_50};border:1px solid {GRAY_200};
                border-radius:9px;padding:0 10px;font-size:12px;
            }}
            QLineEdit:focus {{ border-color:{VIOLET_500}; }}
        """)
        add_btn = QPushButton("Add")
        add_btn.setFixedHeight(36)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background:{VIOLET_600};color:white;border:none;
                border-radius:9px;padding:0 14px;font-size:12px;font-weight:600;
            }}
            QPushButton:hover {{ background:{VIOLET_500}; }}
        """)
        add_btn.clicked.connect(self._add_class)
        self._add_input.returnPressed.connect(self._add_class)
        add_row.addWidget(self._add_input, 1)
        add_row.addWidget(add_btn)
        cl.addLayout(add_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{GRAY_200};border:none;max-height:1px;")
        cl.addWidget(sep)

        # Rename class
        rename_lbl = QLabel("Rename Class")
        rename_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{GRAY_700};background:transparent;border:none;")
        cl.addWidget(rename_lbl)

        self._rename_from = QComboBox()
        self._rename_from.setFixedHeight(36)
        self._rename_from.setStyleSheet(f"""
            QComboBox {{
                background:{GRAY_50};border:1px solid {GRAY_200};
                border-radius:9px;padding:0 10px;font-size:12px;color:{GRAY_700};
            }}
        """)
        cl.addWidget(self._rename_from)

        self._rename_to = QLineEdit()
        self._rename_to.setPlaceholderText("New name…")
        self._rename_to.setFixedHeight(36)
        self._rename_to.setStyleSheet(self._add_input.styleSheet())
        cl.addWidget(self._rename_to)

        rename_btn = QPushButton("Rename Class")
        rename_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rename_btn.setStyleSheet(f"""
            QPushButton {{
                background:{EMERALD_50};color:{EMERALD_600};
                border:1px solid {EMERALD_200};border-radius:9px;
                padding:8px;font-size:12px;font-weight:600;
            }}
            QPushButton:hover {{ background:#D1FAE5; }}
        """)
        rename_btn.clicked.connect(self._rename_class)
        cl.addWidget(rename_btn)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"background:{GRAY_200};border:none;max-height:1px;")
        cl.addWidget(sep2)

        delete_lbl = QLabel("Delete Class")
        delete_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{GRAY_700};background:transparent;border:none;")
        cl.addWidget(delete_lbl)

        self._delete_combo = QComboBox()
        self._delete_combo.setFixedHeight(36)
        self._delete_combo.setStyleSheet(self._rename_from.styleSheet())
        cl.addWidget(self._delete_combo)

        del_btn = QPushButton("Delete Class")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background:{RED_50};color:{RED_600};
                border:1px solid {RED_200};border-radius:9px;
                padding:8px;font-size:12px;font-weight:600;
            }}
            QPushButton:hover {{ background:#FEE2E2; }}
        """)
        del_btn.clicked.connect(self._delete_class)
        cl.addWidget(del_btn)
        cl.addStretch()

    def refresh(self):
        cl = self._list_card.content_layout()
        while cl.count():
            item = cl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        p = self._state.project
        if not p:
            return

        self._rename_from.blockSignals(True)
        self._delete_combo.blockSignals(True)
        self._rename_from.clear()
        self._delete_combo.clear()

        for lbl in p.labels:
            self._rename_from.addItem(lbl)
            self._delete_combo.addItem(lbl)

        self._rename_from.blockSignals(False)
        self._delete_combo.blockSignals(False)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent;border:none;")
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        wl = QVBoxLayout(w)
        wl.setSpacing(6)
        wl.setContentsMargins(0, 0, 0, 0)

        for i, lbl in enumerate(p.labels):
            row = QWidget()
            row.setStyleSheet(f"""
                QWidget {{
                    background:{GRAY_50};border:1px solid {GRAY_200};border-radius:10px;
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 8, 12, 8)
            rl.setSpacing(10)

            color_dot = QLabel()
            color_dot.setFixedSize(16, 16)
            color = CLASS_COLORS[i % len(CLASS_COLORS)]
            color_dot.setStyleSheet(
                f"background:{color};border-radius:8px;border:none;"
            )
            lbl_widget = QLabel(lbl)
            lbl_widget.setStyleSheet(
                f"font-size:13px;font-weight:600;color:{GRAY_900};"
                f"background:transparent;border:none;"
            )
            count_lbl = QLabel(
                f"{sum(1 for ann in (ann for img in p.images for ann in img.annotations) if ann.label == lbl)} annotations"
            )
            count_lbl.setStyleSheet(f"font-size:10px;color:{GRAY_400};background:transparent;border:none;")
            rl.addWidget(color_dot)
            rl.addWidget(lbl_widget, 1)
            rl.addWidget(count_lbl)
            wl.addWidget(row)

        if not p.labels:
            empty = QLabel("No classes defined yet.\nAdd classes or annotate images.")
            empty.setStyleSheet(f"font-size:12px;color:{GRAY_400};background:transparent;border:none;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wl.addWidget(empty)

        wl.addStretch()
        scroll.setWidget(w)
        cl.addWidget(scroll, 1)

    def _add_class(self):
        label = self._add_input.text().strip()
        if label:
            self._state.add_class(label)
            self._add_input.clear()

    def _rename_class(self):
        old = self._rename_from.currentText()
        new = self._rename_to.text().strip()
        if old and new and old != new:
            self._state.rename_class(old, new)
            self._rename_to.clear()

    def _delete_class(self):
        label = self._delete_combo.currentText()
        if label:
            self._state.delete_class(label)


RED_200 = "#FECACA"
RED_600 = "#DC2626"
