import json
from datetime import datetime
from pathlib import Path
from app.database.engine import get_session
from app.database.models import Project, Log


PROJECTS_DIR = Path.home() / ".inspectx" / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def _log_time():
    return datetime.now().strftime("%H:%M:%S")


def get_all_projects(user_id: int):
    with get_session() as session:
        projects = (
            session.query(Project)
            .filter_by(user_id=user_id)
            .order_by(Project.updated_at.desc())
            .all()
        )
        # Eagerly load all needed relationships before expunging
        for p in projects:
            _ = p.images
            for img in p.images:
                _ = img.annotations
            _ = p.versions
            _ = p.ml_models
            _ = p.logs
        session.expunge_all()
        return projects


def get_project(project_id: int):
    with get_session() as session:
        p = session.query(Project).filter_by(id=project_id).first()
        if p:
            # Trigger eager load of all relationships
            _ = p.images
            for img in p.images:
                _ = img.annotations
            _ = p.versions
            for v in p.versions:
                _ = v.version_images
            _ = p.ml_models
            _ = p.logs
            session.expunge_all()
        return p


def create_project(user_id: int, name: str, project_type: str) -> Project:
    with get_session() as session:
        p = Project(
            user_id=user_id,
            name=name,
            type=project_type,
            status="Active",
            source="No Data",
            updated_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        if project_type == "segmentation":
            p.labels = ["scratch", "dent", "stain", "crack"]
        else:
            p.labels = ["scratch", "missing-part", "contamination"]
        session.add(p)
        session.flush()

        log = Log(
            project_id=p.id,
            log_type="System",
            time_str=_log_time(),
            message="Project created",
        )
        session.add(log)
        session.commit()
        session.refresh(p)
        session.expunge(p)

        project_dir = PROJECTS_DIR / str(p.id) / "images"
        project_dir.mkdir(parents=True, exist_ok=True)
        return p


def patch_project(project_id: int, **kwargs):
    with get_session() as session:
        p = session.query(Project).filter_by(id=project_id).first()
        if not p:
            return
        for key, value in kwargs.items():
            if key == "labels":
                p.labels = value
            elif key == "tags":
                p.tags = value
            elif key == "camera":
                p.camera = value
            elif key == "communication":
                p.communication = value
            elif key == "runtime":
                p.runtime = value
            elif key == "signals":
                p.signals = value
            else:
                setattr(p, key, value)
        p.updated_at = datetime.utcnow()
        session.commit()


def delete_project(project_id: int):
    with get_session() as session:
        p = session.query(Project).filter_by(id=project_id).first()
        if p:
            session.delete(p)
            session.commit()


def add_log(project_id: int, log_type: str, message: str):
    with get_session() as session:
        log = Log(
            project_id=project_id,
            log_type=log_type,
            time_str=_log_time(),
            message=message,
        )
        session.add(log)
        session.commit()


def get_project_image_dir(project_id: int) -> Path:
    d = PROJECTS_DIR / str(project_id) / "images"
    d.mkdir(parents=True, exist_ok=True)
    return d
