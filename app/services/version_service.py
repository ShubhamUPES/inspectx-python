from datetime import datetime
from app.database.engine import get_session
from app.database.models import Version, VersionImage, Project, Image


def generate_version(project_id: int) -> int:
    with get_session() as session:
        p = session.query(Project).filter_by(id=project_id).first()
        if not p:
            return None

        images = session.query(Image).filter_by(project_id=project_id).all()
        if not images:
            return None

        count = session.query(Version).filter_by(project_id=project_id).count()
        name = f"Version {count + 1}"
        annotated = sum(1 for img in images if img.status == "Annotated")

        v = Version(
            project_id=project_id,
            name=name,
            snapshot_name=f"{p.name.replace(' ', '_')}_snapshot_v{count + 1}",
            created_at=datetime.utcnow(),
            image_count=len(images),
            annotated_count=annotated,
            generated_count=len(images) * 3,
            notes="Generated from current working dataset.",
            split_ratio="80 / 15 / 5",
            ready=True,
        )
        v.preprocessing = ["Auto Orient", "Resize 640", "CLAHE"]
        v.augmentation = ["Flip", "Rotate", "Blur", "Noise", "Brightness"]
        v.transforms = ["Normalize", "Pad to square"]
        session.add(v)
        session.flush()

        for img in images:
            link = VersionImage(version_id=v.id, image_id=img.id)
            session.add(link)

        p.active_version_id = v.id
        p.updated_at = datetime.utcnow()
        session.commit()
        return v.id


def get_version(version_id: int):
    with get_session() as session:
        v = session.query(Version).filter_by(id=version_id).first()
        if v:
            _ = v.version_images
            session.expunge_all()
        return v


def get_project_versions(project_id: int) -> list:
    with get_session() as session:
        versions = (
            session.query(Version)
            .filter_by(project_id=project_id)
            .order_by(Version.created_at.desc())
            .all()
        )
        for v in versions:
            _ = v.version_images
        session.expunge_all()
        return versions


def set_active_version(project_id: int, version_id: int):
    with get_session() as session:
        p = session.query(Project).filter_by(id=project_id).first()
        if p:
            p.active_version_id = version_id
            p.updated_at = datetime.utcnow()
            session.commit()
