"""
AppState — central reactive state for the InspectX desktop app.

Holds the current user and project; exposes signals that pages subscribe to.
All mutations go through state methods so the UI stays in sync.
"""
from __future__ import annotations
import random
import time
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from app.database.engine import init_db
from app.services import (
    auth_service,
    project_service,
    image_service,
    annotation_service,
    version_service,
    model_service,
)


# ── Background training worker ─────────────────────────────────────────────────

class _TrainingWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str, str, str)   # map, precision, recall, latency

    def run(self):
        steps = 40
        for i in range(steps + 1):
            time.sleep(0.06)
            self.progress.emit(int(i / steps * 100))
        map_s     = f"{random.randint(82, 97)}%"
        prec      = f"{random.randint(85, 98)}%"
        rec       = f"{random.randint(80, 96)}%"
        lat       = f"{random.randint(12, 28)} ms"
        self.finished.emit(map_s, prec, rec, lat)


# ── AppState ───────────────────────────────────────────────────────────────────

class AppState(QObject):
    # Emitted whenever the active project (or its data) changes
    project_changed = pyqtSignal()
    # Emitted for toast notifications
    notification    = pyqtSignal(str)
    # Training signals
    training_progress = pyqtSignal(int)
    training_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        init_db()
        auth_service.ensure_demo_user()

        self.user    = None
        self.project = None
        self._training_worker: _TrainingWorker | None = None
        self._training_version_id: int | None = None
        self._training_version_name: str = ""

    # ── Auth ───────────────────────────────────────────────────────────────────

    def set_user(self, user):
        self.user = user

    def logout(self):
        self.user    = None
        self.project = None

    # ── Project management ─────────────────────────────────────────────────────

    def load_projects(self) -> list:
        if not self.user:
            return []
        return project_service.get_all_projects(self.user.id)

    def open_project(self, project_id: int):
        self.project = project_service.get_project(project_id)
        self.project_changed.emit()

    def reload_project(self):
        if self.project:
            self.project = project_service.get_project(self.project.id)
            self.project_changed.emit()

    def create_project(self, name: str, project_type: str):
        if not self.user:
            return
        p = project_service.create_project(self.user.id, name, project_type)
        self.open_project(p.id)

    def delete_project(self, project_id: int):
        project_service.delete_project(project_id)
        if self.project and self.project.id == project_id:
            self.project = None
            self.project_changed.emit()

    # ── Image management ───────────────────────────────────────────────────────

    def add_images(self, file_paths: list):
        if not self.project:
            return
        image_service.add_images_from_paths(self.project.id, file_paths)
        self.reload_project()

    def select_image(self, image_id: int):
        if not self.project:
            return
        image_service.set_selected_image(self.project.id, image_id)
        self.reload_project()

    def delete_images(self, image_ids: list):
        image_service.delete_images(image_ids)
        self.reload_project()

    def get_selected_image(self):
        if not self.project or not self.project.selected_image_id:
            return None
        return image_service.get_image(self.project.selected_image_id)

    # ── Annotation management ──────────────────────────────────────────────────

    def add_annotation(self, image_id: int, ann_type: str,
                       x: float, y: float, w: float, h: float,
                       points: list | None = None) -> int:
        ann_id = annotation_service.add_annotation(
            image_id, ann_type, x, y, w, h, points
        )
        self.reload_project()
        return ann_id

    def assign_label(self, annotation_id: int, label: str):
        if not self.project:
            return
        annotation_service.assign_label(annotation_id, label, self.project.id)
        self.reload_project()

    def update_annotation(self, annotation_id: int,
                          x: float, y: float, w: float, h: float,
                          points: list | None = None):
        annotation_service.update_annotation(annotation_id, x, y, w, h, points)

    def delete_annotation(self, annotation_id: int, image_id: int):
        annotation_service.delete_annotation(annotation_id, image_id)
        self.reload_project()

    def get_annotations(self, image_id: int) -> list:
        return annotation_service.get_annotations(image_id)

    # ── Class management ───────────────────────────────────────────────────────

    def add_class(self, label: str):
        if not self.project:
            return
        labels = list(self.project.labels)
        if label not in labels:
            labels.append(label)
            project_service.patch_project(self.project.id, labels=labels)
            self.reload_project()

    def rename_class(self, old: str, new: str):
        if not self.project:
            return
        labels = [new if l == old else l for l in self.project.labels]
        project_service.patch_project(self.project.id, labels=labels)
        # Also rename on annotations (best-effort)
        for img in self.project.images:
            for ann in img.annotations:
                if ann.label == old:
                    annotation_service.assign_label(ann.id, new, self.project.id)
        self.reload_project()

    def delete_class(self, label: str):
        if not self.project:
            return
        labels = [l for l in self.project.labels if l != label]
        project_service.patch_project(self.project.id, labels=labels)
        self.reload_project()

    # ── Version management ─────────────────────────────────────────────────────

    def generate_version(self):
        if not self.project:
            return
        version_service.generate_version(self.project.id)
        project_service.add_log(
            self.project.id, "Version",
            f"Dataset version generated from {len(self.project.images)} images."
        )
        self.reload_project()
        self.notify("Dataset version generated.")

    def active_version(self):
        if not self.project or not self.project.active_version_id:
            return None
        return version_service.get_version(self.project.active_version_id)

    def set_active_version(self, version_id: int):
        if not self.project:
            return
        version_service.set_active_version(self.project.id, version_id)
        self.reload_project()

    # ── Model management ───────────────────────────────────────────────────────

    def active_model(self):
        if not self.project or not self.project.active_model_id:
            return None
        models = model_service.get_project_models(self.project.id)
        return next((m for m in models if m.id == self.project.active_model_id), None)

    def promote_model(self, model_id: int):
        if not self.project:
            return
        model_service.promote_model(self.project.id, model_id)
        self.reload_project()
        self.notify("Model promoted to Production.")

    def delete_model(self, model_id: int):
        model_service.delete_model(model_id)
        self.reload_project()
        self.notify("Model deleted.")

    # ── Training ───────────────────────────────────────────────────────────────

    def start_training(self, version_id: int, version_name: str):
        self._training_version_id   = version_id
        self._training_version_name = version_name
        self._training_worker = _TrainingWorker()
        self._training_worker.progress.connect(self.training_progress)
        self._training_worker.finished.connect(self._on_training_done)
        self._training_worker.start()

    def _on_training_done(self, map_s: str, prec: str, rec: str, lat: str):
        if not self.project:
            return
        model_service.add_model(
            project_id    = self.project.id,
            version_id    = self._training_version_id,
            version_name  = self._training_version_name,
            map_score     = map_s,
            precision     = prec,
            recall        = rec,
            latency       = lat,
        )
        project_service.add_log(
            self.project.id, "Model",
            f"Training complete. mAP: {map_s}  Precision: {prec}  Recall: {rec}  Latency: {lat}"
        )
        self.reload_project()
        self.training_finished.emit()
        self.notify(f"Training complete — mAP {map_s}")

    # ── Inference (simulated) ──────────────────────────────────────────────────

    def run_inspection(self) -> dict:
        """Simulate inference and return a result dict."""
        labels = self.project.labels if self.project else ["defect"]
        n_obj  = random.randint(0, 4)
        if n_obj == 0:
            decision = "PASS"
        else:
            decision = "FAIL"
        return {
            "decision":   decision,
            "confidence": f"{random.randint(82, 99)}%",
            "inference":  f"{random.randint(8, 26)} ms",
            "objects":    str(n_obj),
            "labels":     random.sample(labels, min(n_obj, len(labels))),
        }

    # ── Notifications ──────────────────────────────────────────────────────────

    def notify(self, message: str):
        self.notification.emit(message)
