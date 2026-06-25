from app.database.engine import get_session
from app.database.models import Annotation, Image, Project


def add_annotation(image_id: int, ann_type: str, x: float, y: float,
                   w: float, h: float, points: list = None) -> int:
    with get_session() as session:
        ann = Annotation(
            image_id=image_id,
            ann_type=ann_type,
            x=x, y=y, w=w, h=h,
            pending=True,
        )
        if points:
            ann.points = points
        session.add(ann)
        session.commit()
        return ann.id


def assign_label(annotation_id: int, label: str, project_id: int):
    """Assign label to annotation and update image/project label lists."""
    with get_session() as session:
        ann = session.query(Annotation).filter_by(id=annotation_id).first()
        if not ann:
            return
        ann.label = label.strip()
        ann.pending = False

        img = session.query(Image).filter_by(id=ann.image_id).first()
        if img:
            labels = img.labels
            if ann.label not in labels:
                labels.append(ann.label)
            img.labels = labels
            img.status = "Annotated"

            p = session.query(Project).filter_by(id=project_id).first()
            if p:
                proj_labels = p.labels
                if ann.label not in proj_labels:
                    proj_labels.append(ann.label)
                p.labels = proj_labels

        session.commit()


def update_annotation(annotation_id: int, x: float, y: float,
                      w: float, h: float, points: list = None):
    with get_session() as session:
        ann = session.query(Annotation).filter_by(id=annotation_id).first()
        if ann:
            ann.x, ann.y, ann.w, ann.h = x, y, w, h
            if points is not None:
                ann.points = points
            session.commit()


def delete_annotation(annotation_id: int, image_id: int):
    with get_session() as session:
        ann = session.query(Annotation).filter_by(id=annotation_id).first()
        if ann:
            session.delete(ann)
            session.flush()

            img = session.query(Image).filter_by(id=image_id).first()
            if img:
                remaining = session.query(Annotation).filter_by(image_id=image_id).count()
                img.status = "Annotated" if remaining > 0 else "Unannotated"
            session.commit()


def get_annotations(image_id: int) -> list:
    with get_session() as session:
        anns = session.query(Annotation).filter_by(image_id=image_id).all()
        result = [a.to_dict() for a in anns]
        return result
