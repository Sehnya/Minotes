from fileinput import filename
from typing import Any

from flask import Flask, render_template, request, jsonify, abort, redirect, url_for, flash, session, jsonify
import logging

from forms import MyForm
from database import User, Note, db
from flask_cors import CORS
import os
from datetime import timedelta

# import flask class, instance of class will be the app
app = Flask(__name__)
app.secret_key = "Elija11052017!"
app.permanent_session_lifetime = timedelta(days=7)

CORS(app, supports_credentials=True)
#instance of class; __name__ helps Flask locate resources like templates and static files.
@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()

@app.route('/', methods=['GET'])
#route() decorator tells flask what URL should trigger our func
def index():
    if "user" in session:
        redirect(url_for("dashboard")) #Already logged in --> go to dash
    return render_template("index.html") # Not logged in --> landing page

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = MyForm()
    if form.validate_on_submit():
        logger.info("Signup form submitted with valid data.")
        try:
            new_user = User.create(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            logger.info(f"User '{new_user.username}' created successfully.")
            flash('Signup successful.')
            return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            flash(f'Error creating user: {e}')
    else:
        if request.method == "POST":
            logger.warning("Form submission failed validation.")
            logger.debug(f"Form errors: {form.errors}")
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET','POST'])
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
    flash("You have been logged out.")
    return redirect(url_for("login"))

@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    user = User.get_or_none(User.username == session["user"])
    notes = Note.select().where(Note.user == user)
    return render_template('dashboard.html', user=user, notes=notes)


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
@app.route('/home', methods=['GET','POST'])
def home():
    if "user" not in session:
        flash('Please log in to continue.')
        return redirect(url_for('login'))

    user = User.get_or_none(User.username == session["user"])

    if request.method == "POST":
        # Example: Create a note directly from dashboard
        title = request.form.get("title")
        content = request.form.get("content")
        if title and content:
            Note.create(title=title, content=content, user=user)
            flash("Note created!")
        return redirect(url_for("home"))

    notes = Note.select().where(Note.user == user)
    return render_template("dashboard.html", user=user, notes=notes)

#returns what we want displayed in the browser; content type = HTML
@app.route('/user/<username>')
def user(username):
    user = User.get_or_none(User.username == username)
    if user is None:
        abort(404, description="User not found")

    else: return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })


#Retrieve all notes for a user
@app.route('/user/<username>/notes', methods=['POST'])
def create_note(username):
   user = User.get_or_none(User.username == username)
   if user is None:
       abort(404, description="User not found")

   data = request.get_json()
   title = data.get("title")
   content = data.get("content")

   if not title or not content:
     abort(400, description="Title and content required")

   note = Note.create(title=title, content=content, user=user)
   return jsonify({"id": note.id, "message": "Note created"}), 201


@app.route('/user/<username>/notes/<int:note_id>', methods=['PUT'])
def update_note(username,note_id):
    user = User.get_or_none(User.username == username)
    if user is None:
        abort(404, description="User not found")

    note = Note.get_or_none((Note.id == note_id) & (Note.user == user))
    if note is None:
        abort(404, description="Note not found")

    data = request.get_json()
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    note.save()

    return jsonify({ "message": "Note updated"}), 200

from flask import request

from flask import request

@app.route('/user/<username>/notes/<int:note_id>', methods=['DELETE'])
def delete_note(username, note_id):
    ip = request.remote_addr
    user = User.get_or_none(User.username == username)
    if not user:
        logger.warning(f"[{ip}] Failed delete attempt - User '{username}' not found.")
        return jsonify({"error": "User not found"}), 404

    note = Note.get_or_none((Note.id == note_id) & (Note.user == user))
    if not note:
        logger.warning(f"[{ip}] Note {note_id} not found for user '{username}'.")
        return jsonify({"error": "Note not found"}), 404

    note.delete_instance()
    logger.info(f"[{ip}] User '{username}' deleted note {note_id}.")

    return jsonify({"message": "Note deleted successfully", "note_id": note_id}), 200




from flask import request, jsonify, session
from app.database import User, Note
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@app.route("/save_note", methods=["POST"])
def save_note():
    if "user" not in session:
        logger.warning("Unauthorized save_note attempt")
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    if not user:
        logger.warning("User not found during save_note")
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not title or not content:
        return jsonify({"message": "Title and content required"}), 400

    # Check if a note with the same title exists for this user
    existing_note = Note.get_or_none((Note.title == title) & (Note.user == user))

    if existing_note:
        logger.info(f"Updating note (ID: {existing_note.id}) for user: {user.username}")
        existing_note.content = content
        existing_note.updated_at = datetime.utcnow()
        existing_note.save()
        return jsonify({
            "message": "Note updated successfully.",
            "note_id": existing_note.id
        }), 200
    else:
        new_note = Note.create(title=title, content=content, user=user)
        logger.info(f"Created new note (ID: {new_note.id}) for user: {user.username}")
        return jsonify({
            "message": "Note saved successfully.",
            "note_id": new_note.id
        }), 200

@app.route("/api/notes")
def api_notes():
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    notes = Note.select().where(Note.user == user)

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





logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",  # Timestamp and level
    handlers=[           # Save to file
        logging.StreamHandler()                        # Output to console (for Render logs)
    ]
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    from waitress import serve
    port = int(os.environ.get('PORT', 5000))
    serve(app, host="0.0.0.0", port=port)