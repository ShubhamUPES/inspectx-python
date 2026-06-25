import shutil
from datetime import datetime
from pathlib import Path
from app.database.engine import get_session
from app.database.models import Image, Project
from app.services.project_service import get_project_image_dir


def add_images_from_paths(project_id: int, file_paths: list, source: str = "Upload") -> list:
    """Copy files into project storage, create Image records."""
    dest_dir = get_project_image_dir(project_id)
    created = []

    with get_session() as session:
        p = session.query(Project).filter_by(id=project_id).first()

        for src_path in file_paths:
            src = Path(src_path)
            if not src.exists():
                continue

            # Avoid name collisions
            dest = dest_dir / src.name
            counter = 1
            while dest.exists():
                dest = dest_dir / f"{src.stem}_{counter}{src.suffix}"
                counter += 1

            shutil.copy2(str(src), str(dest))

            img = Image(
                project_id=project_id,
                name=dest.name,
                file_path=str(dest),
                source=source,
                status="Unannotated",
                split=_auto_split(len(created)),
                created_at=datetime.utcnow(),
            )
            img.tags = ["train"]
            session.add(img)
            session.flush()
            created.append(img.id)

        if p and created:
            p.source = f"Upload: {source}"
            p.updated_at = datetime.utcnow()
            if not p.selected_image_id:
                p.selected_image_id = created[0]

        session.commit()

    return created


def _auto_split(index: int) -> str:
    if index % 8 == 0:
        return "Test"
    if index % 5 == 0:
        return "Valid"
    return "Train"


def get_image(image_id: int):
    with get_session() as session:
        img = session.query(Image).filter_by(id=image_id).first()
        if img:
            _ = img.annotations
            session.expunge_all()
        return img


def delete_images(image_ids: list):
    with get_session() as session:
        for iid in image_ids:
            img = session.query(Image).filter_by(id=iid).first()
            if img:
                if img.file_path and Path(img.file_path).exists():
                    try:
                        Path(img.file_path).unlink()
                    except Exception:
                        pass
                session.delete(img)
        session.commit()


def set_selected_image(project_id: int, image_id: int):
    with get_session() as session:
        p = session.query(Project).filter_by(id=project_id).first()
        if p:
            p.selected_image_id = image_id
            p.updated_at = datetime.utcnow()
            session.commit()


def patch_image(image_id: int, **kwargs):
    with get_session() as session:
        img = session.query(Image).filter_by(id=image_id).first()
        if not img:
            return
        for key, value in kwargs.items():
            if key == "labels":
                img.labels = value
            elif key == "tags":
                img.tags = value
            else:
                setattr(img, key, value)
        session.commit()
