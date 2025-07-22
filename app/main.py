from typing import Any

from flask import Flask, jsonify, abort
from app.database import User, Note,db

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
def hello_world():
    return "<p>Hello, World!</p>"
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
@app.route('/user/<username>/notes')
def get_notes(username):
   user = User.get_or_none(User.username == username)
   if user is None:
       abort(404, description="User not found")

   notes = Note.select().where(Note.user == user)
   notes_data = [{"id": note.id,"title": note.tite,"content": note.content} for note in notes]

   if not notes_data:
       abort(404, description="You don't have any notes")

   return jsonify(notes_data)


@app.route('/user/<username>/notes/<int:note_id>')
def get_note(username,note_id):
    user = User.get_or_none(User.username == username)
    if user is None:
        abort(404, description="User not found")

    note = Note.get_or_none(Note.id == note_id) & (Note.user == user)
    if note is None:
        abort(404, description="Note not found")

    return jsonify({
        "id": note.id,
        "title":note.title,
        "content":note.content
    })

if __name__ == '__main__':
    app.run(debug=True)