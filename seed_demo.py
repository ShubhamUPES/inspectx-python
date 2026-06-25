"""
seed_demo.py — Populate the database with a demo user + sample project data.
Run once before packaging:  python seed_demo.py

Credentials created
-------------------
  Email   : demo@inspectx.ai
  Password: demo1234

  Email   : admin
  Password: admin
"""

import sys
from pathlib import Path

# Make sure imports resolve from project root
sys.path.insert(0, str(Path(__file__).parent))

from app.database.engine import init_db, get_session
from app.database.models import User, Project, Image, Annotation, Version, MLModel, Log
from app.services.auth_service import ensure_demo_user, hash_password
from datetime import datetime, timedelta

def seed():
    print("Initialising database …")
    init_db()

    print("Creating demo users …")
    ensure_demo_user()

    with get_session() as session:
        user = session.query(User).filter_by(email="demo@inspectx.ai").first()

        # Skip if demo project already exists
        if session.query(Project).filter_by(user_id=user.id, name="PCB Defect Detection").first():
            print("Demo data already present — skipping.")
            return

        print("Seeding sample project …")

        # ── Project ───────────────────────────────────────────────────────────
        project = Project(
            user_id=user.id,
            name="PCB Defect Detection",
            type="detection",
            status="Active",
            source="Uploaded",
            updated_at=datetime.utcnow(),
            created_at=datetime.utcnow() - timedelta(days=5),
            labels_json='["scratch","solder_bridge","missing_pad","burn_mark"]',
            tags_json='["train","review","failed-sample","production"]',
        )
        session.add(project)
        session.flush()  # get project.id

        # ── Sample images (metadata only — no real files needed for demo) ─────
        statuses = ["Annotated", "Annotated", "Unannotated", "Annotated", "Unannotated"]
        splits   = ["Train",     "Train",      "Val",          "Train",     "Test"]
        for i, (st, sp) in enumerate(zip(statuses, splits), start=1):
            img = Image(
                project_id=project.id,
                name=f"pcb_sample_{i:03d}.jpg",
                file_path="",          # no physical file; UI will show placeholder
                status=st,
                split=sp,
                source="Upload",
                created_at=datetime.utcnow() - timedelta(hours=i * 3),
            )
            session.add(img)
            session.flush()

            if st == "Annotated":
                ann = Annotation(
                    image_id=img.id,
                    ann_type="bbox",
                    label="scratch",
                    x=0.1 + i * 0.05,
                    y=0.2,
                    w=0.15,
                    h=0.12,
                )
                session.add(ann)

        # ── Dataset version ───────────────────────────────────────────────────
        version = Version(
            project_id=project.id,
            name="v1.0 — Initial",
            snapshot_name="v1.0",
            image_count=5,
            annotated_count=3,
            generated_count=0,
            notes="First labelled batch from line A.",
            split_ratio="80 / 15 / 5",
            ready=True,
            created_at=datetime.utcnow() - timedelta(days=2),
        )
        session.add(version)
        session.flush()

        # ── Trained model ─────────────────────────────────────────────────────
        model = MLModel(
            project_id=project.id,
            version_id=version.id,
            name="YOLOv8-nano",
            version_label="v1",
            dataset_version="v1.0",
            map_score="87.4%",
            precision="91.2%",
            recall="83.6%",
            latency="18 ms",
            deployment="Registry",
            trained_at=datetime.utcnow() - timedelta(days=1),
            updated_at=datetime.utcnow() - timedelta(hours=6),
        )
        session.add(model)
        session.flush()

        project.active_model_id   = model.id
        project.active_version_id = version.id

        # ── Activity log ──────────────────────────────────────────────────────
        entries = [
            ("info",    "Model v1 deployed to Registry"),
            ("success", "Training completed — mAP 87.4%"),
            ("info",    "Dataset version v1.0 created (5 images)"),
            ("info",    "Project created"),
        ]
        for i, (kind, msg) in enumerate(entries):
            session.add(Log(
                project_id=project.id,
                log_type=kind,
                time_str=(datetime.utcnow() - timedelta(hours=i * 4)).strftime("%H:%M"),
                message=msg,
                created_at=datetime.utcnow() - timedelta(hours=i * 4),
            ))

        session.commit()

    print("\n✅  Demo data seeded successfully!")
    print("   Login  →  demo@inspectx.ai  /  demo1234")
    print("   Admin  →  admin  /  admin")


if __name__ == "__main__":
    seed()
