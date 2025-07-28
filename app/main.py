import logging
import os
from datetime import timedelta, datetime, timezone

from flask import Flask, render_template, abort, redirect, url_for, flash, session, jsonify, request
from flask_cors import CORS

from database import User, Note, db
from forms import MyForm

app = Flask(__name__)
app.secret_key = "Elija11052017!"
app.permanent_session_lifetime = timedelta(days=7)

CORS(app, supports_credentials=True, origins='*')

logger = logging.getLogger(__name__)


@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect()


@app.teardown_request
def _db_close(exc):
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
                password=form.password.data
            )
            session["user"] = form.username.data
            flash("Signup successful!")
            return redirect(url_for("dashboard"))
        except Exception as e:
            logger.error(f"Signup error: {e}")
            flash("Something went wrong. Please try again.")

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.get_or_none(User.username == username, User.password == password)

        if user and user.password == password:
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
    notes = Note.select().where(Note.user == user)
    return render_template('vue_dashboard.html', user=user, notes=notes)


# API Routes for Vue Frontend
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
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat()
            }
            for note in notes
        ]
    })


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
            "created_at": new_note.created_at.isoformat(),
            "updated_at": new_note.updated_at.isoformat()
        }
    }), 201


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
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
    })


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

    note.title = title
    note.content = content
    note.updated_at = datetime.now(timezone.utc)
    note.save()

    return jsonify({
        "message": "Note updated successfully",
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
    })


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
