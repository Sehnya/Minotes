import logging
import os
from datetime import timedelta, datetime, timezone

from flask import Flask, render_template, abort, redirect, url_for, flash, session, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect

from .database import User, Note, db
from .forms import MyForm

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.permanent_session_lifetime = timedelta(days=7)

# Enable CSRF protection for form submissions.
csrf = CSRFProtect(app)

CORS(app, supports_credentials=True)

logger = logging.getLogger(__name__)


def _iso(value):
    """Return ISO 8601 string for datetime-like values, passthrough otherwise."""
    try:
        return value.isoformat()
    except Exception:
        return str(value)


@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect()


@app.teardown_request
def _db_close(exc):
    # In testing mode with in-memory SQLite, avoid closing the DB to preserve data across requests
    if os.environ.get("TESTING") == "1":
        return
    if not db.is_closed():
        db.close()


@app.route('/', methods=['GET'])
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = MyForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            User.create(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data)
            )
            session["user"] = form.username.data
            session.permanent = True
            flash("Signup successful!")
            return redirect(url_for("dashboard"))
        except Exception as e:
            logger.error(f"Signup error: {e}")
            flash("Something went wrong. Please try again.")

    return render_template('signup.html', form=form)


@csrf.exempt
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.get_or_none(User.username == username)

        if user and check_password_hash(user.password_hash, password):
            session["user"] = username
            session.permanent = True
            return redirect("dashboard")
        else:
            flash("Invalid credentials. Please try again.")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.get_or_none(User.username == session["user"])
    if not user:
        return redirect(url_for("login"))

    # Convert Peewee query to list of dictionaries
    notes_query = Note.select().where((Note.user == user) & (Note.is_active == True)).order_by(Note.updated_at.desc())
    notes_data = []

    for note in notes_query:
        notes_data.append({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': _iso(note.created_at),
            'updated_at': _iso(note.updated_at),
            'version': note.version,
            'parent_id': note.parent.id if note.parent_id else None
        })

    return render_template('vue_dashboard.html', user=user, notes=notes_data)

# API Routes for Vue Frontend
@csrf.exempt
@app.route("/api/session")
def api_session():
    username = session.get("user")
    if not username:
        return jsonify({"logged_in": False}), 401

    user = User.get_or_none(User.username == username)
    if not user:
        return jsonify({"logged_in": False}), 404

    return jsonify({
        "logged_in": True,
        "username": user.username,
        "email": user.email,
        "user_id": user.id,
    })


@csrf.exempt
@app.route("/api/notes", methods=['GET'])
def api_notes():
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    if not user:
        return jsonify({"message": "User not found"}), 404

    notes = Note.select().where((Note.user == user) & (Note.is_active == True)).order_by(Note.updated_at.desc())

    return jsonify({
        "notes": [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_at": _iso(note.created_at),
                "updated_at": _iso(note.updated_at),
                "version": note.version,
                "parent_id": note.parent.id if note.parent_id else None
            }
            for note in notes
        ]
    })


@csrf.exempt
@app.route("/api/notes", methods=['POST'])
def api_create_note():
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    title = data.get("title", "Untitled Note").strip()
    content = data.get("content", "").strip()

    new_note = Note.create(title=title, content=content, user=user)

    return jsonify({
        "message": "Note created successfully",
        "note": {
            "id": new_note.id,
            "title": new_note.title,
            "content": new_note.content,
            "created_at": _iso(new_note.created_at),
            "updated_at": _iso(new_note.updated_at)
        }
    }), 201


@csrf.exempt
@app.route("/api/notes/<int:note_id>", methods=['GET'])
def api_get_note(note_id):
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    if not user:
        return jsonify({"message": "User not found"}), 404

    note = Note.get_or_none((Note.id == note_id) & (Note.user == user) & (Note.is_active == True))
    if not note:
        return jsonify({"message": "Note not found"}), 404

    return jsonify({
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": _iso(note.created_at),
            "updated_at": _iso(note.updated_at),
            "version": note.version,
            "parent_id": note.parent.id if note.parent_id else None
        }
    })


@csrf.exempt
@app.route("/api/notes/<int:note_id>", methods=['PUT'])
def api_update_note(note_id):
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    if not user:
        return jsonify({"message": "User not found"}), 404

    note = Note.get_or_none((Note.id == note_id) & (Note.user == user) & (Note.is_active == True))
    if not note:
        return jsonify({"message": "Note not found"}), 404

    data = request.get_json()
    title = data.get("title", note.title).strip()
    content = data.get("content", note.content).strip()

    # Versioning: create a new version and mark current inactive
    try:
        next_version = (note.version or 1) + 1
        note.is_active = False
        note.save()

        new_note = Note.create(
            title=title,
            content=content,
            user=user,
            parent=note,
            version=next_version,
            is_active=True,
        )

        # Retain only last 5 versions in chain (newest to oldest)
        chain = []
        cur = new_note
        while cur.parent_id is not None:
            chain.append(cur)
            cur = cur.parent
        if len(chain) > 5:
            for old in chain[5:]:
                try:
                    old.delete_instance(recursive=False)
                except Exception as _:
                    logger.warning("Failed pruning old version id=%s", old.id)

        return jsonify({
            "message": "Note updated successfully",
            "note": {
                "id": new_note.id,
                "title": new_note.title,
                "content": new_note.content,
                "created_at": _iso(new_note.created_at),
                "updated_at": _iso(new_note.updated_at),
                "version": new_note.version,
                "parent_id": new_note.parent.id if new_note.parent_id else None
            }
        })
    except Exception as e:
        logger.error("Update/versioning failed: %s", e)
        return jsonify({"message": "Update failed"}), 500


@app.route('/edit_note/<int:note_id>')
def edit_note(note_id):
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.get_or_none(User.username == session["user"])
    if not user:
        return redirect(url_for("login"))

    note = Note.get_or_none((Note.id == note_id) & (Note.user == user) & (Note.is_active == True))
    if not note:
        flash("Note not found")
        return redirect(url_for("dashboard"))

    return render_template('edit_note.html', user=user, note={
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat(),
        'version': note.version,
        'parent_id': note.parent.id if note.parent_id else None
    })


@csrf.exempt
@app.route("/api/notes/<int:note_id>/revert", methods=['POST'])
def api_revert_note(note_id):
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    if not user:
        return jsonify({"message": "User not found"}), 404

    current = Note.get_or_none((Note.id == note_id) & (Note.user == user))
    if not current:
        return jsonify({"message": "Note not found"}), 404

    if not current.parent_id:
        return jsonify({"message": "No previous version to revert to"}), 400

    parent = current.parent

    try:
        next_version = (current.version or 1) + 1
        current.is_active = False
        current.save()

        reverted = Note.create(
            title=parent.title,
            content=parent.content,
            user=user,
            parent=current,
            version=next_version,
            is_active=True,
        )

        return jsonify({
            "message": "Reverted to previous version",
            "note": {
                "id": reverted.id,
                "title": reverted.title,
                "content": reverted.content,
                "created_at": reverted.created_at.isoformat(),
                "updated_at": reverted.updated_at.isoformat(),
                "version": reverted.version,
                "parent_id": reverted.parent.id if reverted.parent_id else None
            }
        })
    except Exception as e:
        logger.error("Revert failed: %s", e)
        return jsonify({"message": "Revert failed"}), 500


@csrf.exempt
@app.route("/api/notes/<int:note_id>", methods=['DELETE'])
def api_delete_note(note_id):
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    if not user:
        return jsonify({"message": "User not found"}), 404

    note = Note.get_or_none((Note.id == note_id) & (Note.user == user))
    if not note:
        return jsonify({"message": "Note not found"}), 404

    note.delete_instance()
    return jsonify({"message": "Note deleted successfully"}), 200


# Keep your existing routes for backward compatibility
@csrf.exempt
@app.route("/save_note", methods=["POST"])
def save_note():
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    note_id = data.get("note_id")

    if not title or not content:
        return jsonify({"message": "Title and content required"}), 400

    if note_id:
        existing_note = Note.get_or_none((Note.id == note_id) & (Note.user == user))
    else:
        existing_note = Note.get_or_none((Note.title == title) & (Note.user == user))

    if existing_note:
        existing_note.title = title
        existing_note.content = content
        existing_note.updated_at = datetime.now(timezone.utc)
        existing_note.save()
        return jsonify({
            "message": "Note updated successfully.",
            "note_id": existing_note.id
        }), 200
    else:
        new_note = Note.create(title=title, content=content, user=user)
        return jsonify({
            "message": "Note saved successfully.",
            "note_id": new_note.id
        }), 200


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

if __name__ == '__main__':
    from waitress import serve

    port = int(os.environ.get('PORT', 5000))
    serve(app, host="0.0.0.0", port=port)
