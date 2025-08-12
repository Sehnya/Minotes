import os
import re
import pytest

# Set testing environment BEFORE importing the app
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.main import app  # noqa: E402
from app.database import db, User  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

@pytest.fixture(scope="session", autouse=True)
def _ensure_db_connected():
    # Keep the connection open for in-memory SQLite
    if db.is_closed():
        db.connect()
    yield
    # Do not close; main.py teardown already skips close when TESTING=1

@pytest.fixture()
def client():
    with app.test_client() as c:
        yield c

@pytest.fixture()
def user_factory():
    created = []
    def _make(username: str = "alice", email: str = "alice@example.com", password: str = "Password123!"):
        u = User.create(username=username, email=email, password_hash=generate_password_hash(password))
        created.append(u)
        return u, password
    return _make


def extract_csrf_token(html: str) -> str:
    # looks for: name="csrf_token" value="<token>"
    m = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', html)
    assert m, "CSRF token not found in form HTML"
    return m.group(1)
