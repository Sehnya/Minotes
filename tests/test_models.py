from werkzeug.security import check_password_hash
from app.database import User, Note


def test_user_password_hash(user_factory):
    u, pwd = user_factory()
    assert u.password_hash != pwd
    assert check_password_hash(u.password_hash, pwd)


def test_note_creation_defaults(user_factory):
    u, _ = user_factory(username="bob", email="bob@example.com")
    n = Note.create(title="Hello", content="<p>World</p>", user=u)
    assert n.is_active is True
    assert n.version == 1
    assert n.parent_id is None
