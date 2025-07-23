from typing import Any

from flask import Flask, render_template, request, jsonify, abort, redirect, url_for, flash, session, jsonify
from database import User, Note, db
from flask_cors import CORS
import os

# import flask class, instance of class will be the app
app = Flask(__name__)
app.secret_key = "Elija11052017!"
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
    return render_template("index.html")

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        #Basic Validation
        if not username or not email or not password:
            flash("All fields are required")
            return redirect(url_for('signup'))

        if User.get_or_none(User.username == username):
            flash("Username already exists. Choose another one.")
            return redirect(url_for('signup'))

#Save user to database
        try:
            User.create(username=username, email=email, password=password)
            session["user"] = username
            flash('Signup successful')
            return redirect("login")
        except Exception as e:
            flash (f"An error occurred: {str(e)}")
            return redirect(url_for('signup'))
    return render_template("signup.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.get_or_none(User.username == username, User.password == password)
        
        if user and user.password == password:
            session["user"] = username
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

@app.route('/user/<username>/notes/<int:note_id>', methods=['DELETE'])
def delete_note(username, note_id):
    user = User.get_or_none(User.username == username)
    if user is None:
        abort(404, description="User not found")

    note = Note.get_or_none((Note.id == note_id) & (Note.user == user))
    if note is None:
        abort(404, description="Note not found")

    note.delete_instance()
    return jsonify({"message": "Note deleted"})

@app.route("/save_note", methods=["POST"])
def save_note():
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"message": "Title and content required"}), 400

    Note.create(title=title, content=content, user=user)
    return jsonify({"message": "Note saved successfully."}), 200

@app.route("/api/notes")
def api_notes():
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.get_or_none(User.username == session["user"])
    notes = Note.select().where(Note.user == user)

    return jsonify({
        "notes": [
            {"id": note.id, "title": note.title, "content": note.content}
            for note in notes
        ]
    })


if __name__ == '__main__':
    from waitress import serve
    port = int(os.environ.get('PORT', 5000))
    serve(app, host="0.0.0.0", port=port)