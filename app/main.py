from typing import Any

from flask import Flask, render_template, request, jsonify, abort
from database import User, Note, db

# import flask class, instance of class will be the app
app = Flask(__name__)
#instance of class; __name__ helps Flask locate resources like templates and static files.
@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()

@app.route('/')
#route() decorator tells flask what URL should trigger our func
def index():
    return render_template("index.html")

@app.route('/signup', methods=['GET','POST'])
def signup():
    return render_template("signup.html")
@app.route('/login', methods=['GET','POST'])
def login():
    return render_template("login.html")



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

   note = Note(title=title, content=content)
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

if __name__ == '__main__':
    app.run(debug=True)