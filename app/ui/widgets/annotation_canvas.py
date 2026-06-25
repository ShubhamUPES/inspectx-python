"""
Interactive annotation canvas.
Supports bbox, polygon, select, count, tracking tools.
Displays real images loaded via Pillow/QPixmap.
"""
from __future__ import annotations
import math
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QRect, QPoint, QRectF, QPointF, pyqtSignal, QSize
from PyQt6.QtGui import (
    QPainter, QPixmap, QColor, QPen, QBrush, QFont,
    QCursor, QPolygonF, QPainterPath,
)

# Annotation type colour map (RGBA-ish QColor)
ANN_COLORS: dict[str, tuple[QColor, QColor]] = {
    "bbox":     (QColor(52, 211, 153),  QColor(52, 211, 153, 40)),
    "roi":      (QColor(96, 165, 250),  QColor(96, 165, 250, 30)),
    "count":    (QColor(251, 191, 36),  QColor(251, 191, 36, 40)),
    "tracking": (QColor(96, 165, 250),  QColor(96, 165, 250, 40)),
    "polygon":  (QColor(167, 139, 250), QColor(167, 139, 250, 50)),
    "mask":     (QColor(167, 139, 250), QColor(167, 139, 250, 60)),
}


def _color_for(ann_type: str):
    return ANN_COLORS.get(ann_type, ANN_COLORS["bbox"])


class AnnotationCanvas(QWidget):
    """
    Widget that renders an image and its annotations.
    Emits signals when annotations are created/modified/selected.
    Coordinates are stored as fractions [0,1] relative to the image.
    """
    annotation_created = pyqtSignal(dict)   # new annotation dict (no id yet)
    annotation_changed = pyqtSignal(dict)   # existing annotation updated
    annotation_selected = pyqtSignal(int)   # annotation id or -1 for deselect
    label_requested = pyqtSignal()          # pending label needs assignment

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)

        self._pixmap: QPixmap | None = None
        self._image_path: str = ""
        self._annotations: list[dict] = []
        self._selected_id: int = -1
        self._tool: str = "select"
        self._zoom: float = 1.0

        # Drawing state
        self._drawing = False
        self._draw_start: QPointF | None = None
        self._draw_end: QPointF | None = None
        self._poly_points: list[QPointF] = []

        # Drag/move state
        self._dragging = False
        self._drag_start: QPointF | None = None
        self._drag_ann: dict | None = None
        self._drag_mode: str = "move"   # "move" or "resize"

    # ── Public API ─────────────────────────────────────────────────────────────

    def load_image(self, file_path: str):
        self._image_path = file_path
        if file_path and Path(file_path).exists():
            self._pixmap = QPixmap(file_path)
        else:
            self._pixmap = self._make_placeholder()
        self.update()

    def set_annotations(self, annotations: list[dict]):
        self._annotations = [dict(a) for a in annotations]
        self.update()

    def set_tool(self, tool: str):
        self._tool = tool
        self._poly_points = []
        self._drawing = False
        cursors = {
            "select":   Qt.CursorShape.ArrowCursor,
            "bbox":     Qt.CursorShape.CrossCursor,
            "polygon":  Qt.CursorShape.CrossCursor,
            "count":    Qt.CursorShape.CrossCursor,
            "tracking": Qt.CursorShape.CrossCursor,
            "brush":    Qt.CursorShape.CrossCursor,
            "roi":      Qt.CursorShape.CrossCursor,
        }
        self.setCursor(QCursor(cursors.get(tool, Qt.CursorShape.ArrowCursor)))
        self.update()

    def set_selected(self, ann_id: int):
        self._selected_id = ann_id
        self.update()

    def set_zoom(self, zoom: float):
        self._zoom = max(0.25, min(4.0, zoom))
        self.update()

    def clear_poly(self):
        self._poly_points = []
        self.update()

    # ── Coordinate helpers ─────────────────────────────────────────────────────

    def _image_rect(self) -> QRect:
        """Compute the rect in widget space where the image is drawn (centered, zoomed)."""
        if not self._pixmap:
            return QRect(0, 0, self.width(), self.height())
        pw = self._pixmap.width() * self._zoom
        ph = self._pixmap.height() * self._zoom
        x = (self.width() - pw) / 2
        y = (self.height() - ph) / 2
        return QRect(int(x), int(y), int(pw), int(ph))

    def _widget_to_image(self, pt: QPointF) -> QPointF:
        """Convert widget coordinates to normalised image coordinates [0,1]."""
        r = self._image_rect()
        if r.width() == 0 or r.height() == 0:
            return QPointF(0, 0)
        nx = (pt.x() - r.x()) / r.width()
        ny = (pt.y() - r.y()) / r.height()
        return QPointF(max(0.0, min(1.0, nx)), max(0.0, min(1.0, ny)))

    def _image_to_widget(self, nx: float, ny: float) -> QPointF:
        r = self._image_rect()
        return QPointF(r.x() + nx * r.width(), r.y() + ny * r.height())

    def _ann_rect_widget(self, ann: dict) -> QRectF:
        tl = self._image_to_widget(ann["x"], ann["y"])
        br = self._image_to_widget(ann["x"] + ann["w"], ann["y"] + ann["h"])
        return QRectF(tl, br)

    def _hit_test(self, pt: QPointF) -> dict | None:
        """Return topmost annotation under pt (widget coords)."""
        for ann in reversed(self._annotations):
            r = self._ann_rect_widget(ann)
            if r.contains(pt):
                return ann
        return None

    # ── Paint ──────────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Background
        painter.fillRect(self.rect(), QColor("#0F172A"))

        # Image
        r = self._image_rect()
        if self._pixmap:
            painter.drawPixmap(r, self._pixmap)
        else:
            painter.fillRect(r, QColor("#1e293b"))

        # Existing annotations
        for ann in self._annotations:
            self._draw_annotation(painter, ann, selected=(ann.get("id") == self._selected_id))

        # In-progress drawing
        if self._drawing and self._draw_start and self._draw_end:
            self._draw_draft(painter)

        # Polygon in-progress points
        if self._poly_points and self._tool in ("polygon", "mask"):
            self._draw_poly_draft(painter)

        # Zoom indicator
        painter.setFont(QFont("monospace", 9, QFont.Weight.Bold))
        painter.setPen(QColor("#93C5FD"))
        painter.drawText(r.right() - 60, r.top() + 20, f"Zoom {int(self._zoom*100)}%")

        painter.end()

    def _draw_annotation(self, painter: QPainter, ann: dict, selected: bool):
        stroke, fill = _color_for(ann.get("type", "bbox"))
        if ann.get("type") == "polygon" and ann.get("points"):
            poly = QPolygonF()
            for p in ann["points"]:
                wp = self._image_to_widget(p["x"], p["y"])
                poly.append(wp)
            pen = QPen(QColor("white") if selected else stroke, 2 if selected else 1.5)
            painter.setPen(pen)
            painter.setBrush(QBrush(fill))
            painter.drawPolygon(poly)
            # Label
            if poly.size() > 0:
                lbl = ann.get("label") or ann.get("type", "")
                if lbl:
                    fp = poly.at(0)
                    painter.setPen(QPen(QColor("white")))
                    painter.setFont(QFont("sans-serif", 8, QFont.Weight.Bold))
                    painter.fillRect(QRectF(fp.x(), fp.y() - 14, len(lbl)*7 + 6, 14),
                                     QColor(0, 0, 0, 160))
                    painter.drawText(QPointF(fp.x() + 3, fp.y() - 3), lbl)
        else:
            rect = self._ann_rect_widget(ann)
            pen = QPen(QColor("white") if selected else stroke, 2 if selected else 1.5)
            if selected:
                pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(fill))
            painter.drawRect(rect)
            # Label tag
            lbl = ann.get("label") or ann.get("type", "")
            if lbl:
                painter.setFont(QFont("sans-serif", 8, QFont.Weight.Bold))
                painter.setPen(QPen(QColor("white")))
                tag_rect = QRectF(rect.left(), rect.top() - 16,
                                  len(lbl) * 7 + 8, 16)
                painter.fillRect(tag_rect, QColor(0, 0, 0, 180))
                painter.drawText(QPointF(rect.left() + 4, rect.top() - 4), lbl)

    def _draw_draft(self, painter: QPainter):
        stroke, fill = _color_for(self._tool if self._tool != "brush" else "mask")
        x1, y1 = self._draw_start.x(), self._draw_start.y()
        x2, y2 = self._draw_end.x(), self._draw_end.y()
        rect = QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pen = QPen(stroke, 1.5, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(QBrush(fill))
        painter.drawRect(rect)

    def _draw_poly_draft(self, painter: QPainter):
        stroke, fill = _color_for("polygon")
        pen = QPen(stroke, 1.5)
        painter.setPen(pen)
        for i, p in enumerate(self._poly_points):
            wp = self._image_to_widget(p.x(), p.y())
            painter.setBrush(QBrush(QColor("white")))
            painter.drawEllipse(wp, 4, 4)
            if i > 0:
                prev = self._image_to_widget(self._poly_points[i-1].x(), self._poly_points[i-1].y())
                painter.drawLine(prev, wp)

    @staticmethod
    def _make_placeholder() -> QPixmap:
        px = QPixmap(800, 520)
        px.fill(QColor("#1e293b"))
        p = QPainter(px)
        p.setPen(QPen(QColor("#334155"), 2))
        p.drawLine(0, 0, 800, 520)
        p.drawLine(800, 0, 0, 520)
        p.setFont(QFont("sans-serif", 14))
        p.setPen(QColor("#64748b"))
        p.drawText(QRectF(0, 0, 800, 520), Qt.AlignmentFlag.AlignCenter, "No Image")
        p.end()
        return px

    # ── Mouse events ───────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pt = QPointF(event.position())

        if self._tool == "select":
            ann = self._hit_test(pt)
            if ann:
                self._selected_id = ann.get("id", -1)
                self.annotation_selected.emit(self._selected_id)
                mode = "resize" if (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) else "move"
                self._dragging = True
                self._drag_start = pt
                self._drag_ann = dict(ann)
                self._drag_mode = mode
            else:
                self._selected_id = -1
                self.annotation_selected.emit(-1)
            self.update()
            return

        if self._tool in ("polygon", "mask"):
            img_pt = self._widget_to_image(pt)
            self._poly_points.append(img_pt)
            if len(self._poly_points) >= 4:
                xs = [p.x() for p in self._poly_points]
                ys = [p.y() for p in self._poly_points]
                new_ann = {
                    "type": "polygon",
                    "x": min(xs), "y": min(ys),
                    "w": max(xs) - min(xs), "h": max(ys) - min(ys),
                    "points": [{"x": p.x(), "y": p.y()} for p in self._poly_points],
                    "label": "", "pending": True,
                }
                self._poly_points = []
                self.annotation_created.emit(new_ann)
            self.update()
            return

        # bbox / count / tracking / roi
        self._drawing = True
        self._draw_start = pt
        self._draw_end = pt
        self.update()

    def mouseMoveEvent(self, event):
        pt = QPointF(event.position())
        if self._drawing:
            self._draw_end = pt
            self.update()
        elif self._dragging and self._drag_ann:
            if not self._drag_start:
                return
            dx = (pt.x() - self._drag_start.x()) / max(1, self._image_rect().width())
            dy = (pt.y() - self._drag_start.y()) / max(1, self._image_rect().height())
            ann = dict(self._drag_ann)
            if self._drag_mode == "resize":
                ann["w"] = max(0.02, ann["w"] + dx)
                ann["h"] = max(0.02, ann["h"] + dy)
            else:
                ann["x"] = max(0.0, min(1.0 - ann["w"], ann["x"] + dx))
                ann["y"] = max(0.0, min(1.0 - ann["h"], ann["y"] + dy))
            self._drag_start = pt
            self._drag_ann = ann
            # Update live
            idx = next((i for i, a in enumerate(self._annotations)
                        if a.get("id") == ann.get("id")), -1)
            if idx >= 0:
                self._annotations[idx] = ann
            self.annotation_changed.emit(ann)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self._drawing and self._draw_start and self._draw_end:
            r = self._image_rect()
            if r.width() == 0 or r.height() == 0:
                self._drawing = False
                return
            s = self._widget_to_image(self._draw_start)
            e = self._widget_to_image(self._draw_end)
            x = min(s.x(), e.x())
            y = min(s.y(), e.y())
            w = abs(e.x() - s.x())
            h = abs(e.y() - s.y())
            if w > 0.01 and h > 0.01:
                ann_type = "roi" if self._tool == "roi" else \
                           "mask" if self._tool == "brush" else \
                           "tracking" if self._tool == "tracking" else \
                           "count" if self._tool == "count" else "bbox"
                new_ann = {
                    "type": ann_type,
                    "x": x, "y": y, "w": w, "h": h,
                    "label": "", "pending": True, "points": [],
                }
                self.annotation_created.emit(new_ann)
            self._drawing = False
            self._draw_start = None
            self._draw_end = None
            self.update()

        if self._dragging:
            self._dragging = False
            self._drag_ann = None
            self._drag_start = None

    def mouseDoubleClickEvent(self, event):
        if self._tool in ("polygon", "mask") and self._poly_points:
            if len(self._poly_points) >= 3:
                xs = [p.x() for p in self._poly_points]
                ys = [p.y() for p in self._poly_points]
                new_ann = {
                    "type": "polygon",
                    "x": min(xs), "y": min(ys),
                    "w": max(xs) - min(xs), "h": max(ys) - min(ys),
                    "points": [{"x": p.x(), "y": p.y()} for p in self._poly_points],
                    "label": "", "pending": True,
                }
                self._poly_points = []
                self.annotation_created.emit(new_ann)
            else:
                self._poly_points = []
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.set_zoom(self._zoom + 0.1)
        else:
            self.set_zoom(self._zoom - 0.1)
