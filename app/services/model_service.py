from datetime import datetime
from app.database.engine import get_session
from app.database.models import MLModel, Project


def add_model(project_id: int, version_id: int, version_name: str,
              map_score: str, precision: str, recall: str, latency: str) -> int:
    with get_session() as session:
        p = session.query(Project).filter_by(id=project_id).first()
        count = session.query(MLModel).filter_by(project_id=project_id).count()

        m = MLModel(
            project_id=project_id,
            version_id=version_id,
            name=f"{p.name.replace(' ', '_')}_Model_v{count + 1}",
            version_label=f"Model Version {count + 1}",
            dataset_version=version_name,
            map_score=map_score,
            precision=precision,
            recall=recall,
            latency=latency,
            deployment="Registry",
            trained_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(m)
        session.flush()

        p.active_model_id = m.id
        p.updated_at = datetime.utcnow()
        session.commit()
        return m.id


def get_project_models(project_id: int) -> list:
    with get_session() as session:
        models = (
            session.query(MLModel)
            .filter_by(project_id=project_id)
            .order_by(MLModel.trained_at.desc())
            .all()
        )
        session.expunge_all()
        return models


def promote_model(project_id: int, model_id: int):
    with get_session() as session:
        models = session.query(MLModel).filter_by(project_id=project_id).all()
        for m in models:
            if m.id == model_id:
                m.deployment = "Production"
                m.updated_at = datetime.utcnow()
            elif m.deployment == "Production":
                m.deployment = "Registry"

        p = session.query(Project).filter_by(id=project_id).first()
        if p:
            p.active_model_id = model_id
            p.updated_at = datetime.utcnow()
        session.commit()


def delete_model(model_id: int):
    with get_session() as session:
        m = session.query(MLModel).filter_by(id=model_id).first()
        if m:
            session.delete(m)
            session.commit()
