import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── Resolve DB path ────────────────────────────────────────────────────────────
# When frozen by PyInstaller (sys.frozen is set), the executable lives at
# sys.executable.  We store the DB next to it in a "data/" subfolder so it
# persists across app launches and is easy for users to find / back up.
# In development (plain `python main.py`) we keep the original location so
# nothing in the existing codebase needs to change.

if getattr(sys, "frozen", False):
    # Packaged: put DB beside the .exe / .app, in a "data" subfolder
    APP_DIR = Path(sys.executable).parent / "data"
else:
    # Development: original location next to this file
    APP_DIR = Path(__file__).parent

APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "inspectx.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)
Session = sessionmaker(bind=engine)


def init_db():
    from app.database.models import Base
    Base.metadata.create_all(engine)


def get_session():
    return Session()
