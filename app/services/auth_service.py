import bcrypt
from app.database.engine import get_session
from app.database.models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def login(email: str, password: str):
    """Return User if credentials valid, else None."""
    with get_session() as session:
        user = session.query(User).filter_by(email=email.strip().lower()).first()
        if user and verify_password(password, user.password_hash):
            session.expunge(user)
            return user
    return None


def register(email: str, password: str):
    """Create a new user. Return User on success, raise ValueError on duplicate."""
    with get_session() as session:
        existing = session.query(User).filter_by(email=email.strip().lower()).first()
        if existing:
            raise ValueError("Email already registered")
        user = User(email=email.strip().lower(), password_hash=hash_password(password))
        session.add(user)
        session.commit()
        session.refresh(user)
        session.expunge(user)
        return user


def ensure_demo_user():
    """Create the demo and admin users if they do not exist."""
    with get_session() as session:
        if not session.query(User).filter_by(email="demo@inspectx.ai").first():
            session.add(User(email="demo@inspectx.ai", password_hash=hash_password("demo1234")))
        if not session.query(User).filter_by(email="admin").first():
            session.add(User(email="admin", password_hash=hash_password("admin")))
        session.commit()
