# MiNotes

MiNotes is a simple, full‑stack note‑taking application built with Flask (Python) and Peewee ORM, with a minimal Vue front‑end experience for the dashboard and editing. It supports user accounts and CRUD operations for notes with versioning and auto‑save.

## Purpose
A lightweight personal notes app that:
- Lets users sign up, log in, and manage notes securely.
- Provides a pleasant, responsive UI (mobile‑friendly) with rich‑text editing.
- Exposes a small REST API used by the dashboard and editor.

## Features
- User signup, login, and logout (session‑based)
- Create, read, update, and delete notes
- Rich‑text editing (TipTap) for note content
- Note versioning with revert support
- Responsive pages (home, login, signup, dashboard, editor)
- RESTful JSON API consumed by the dashboard/editor

## Tech Stack
- Backend: Flask, Peewee ORM (PostgreSQL)
- Frontend: Jinja2 templates + Vue 3 for dynamic views
- Server: waitress (for production serving)

## Project Structure
- app/main.py — Flask app and routes (HTML + JSON API)
- app/database.py — Peewee models and DB setup
- app/templates/ — HTML templates (index, login, signup, dashboard, edit note)
- app/static/ — CSS and image assets
- requirements.txt — Python dependencies

## Setup and Startup

### Prerequisites
- Python 3.10+
- PostgreSQL 12+ (unless running in TESTING/SQLite mode)

### Environment Variables
These default to local development values if not provided:
- POSTGRES_DB (default: minotes)
- POSTGRES_USER (default: minotes_user)
- POSTGRES_PASSWORD (no default; must be set for Postgres mode)
- POSTGRES_HOST (default: localhost)
- POSTGRES_PORT (default: 5432)
- SECRET_KEY (default: dev-secret-change-me)
- TESTING (set to 1 to use an in‑memory SQLite DB)

Create a .env file or export them in your shell before running.

### Install
1. Create and activate a virtual environment.
2. Install dependencies:
   pip install -r requirements.txt

### Initialize Database
- On import, database.py connects and creates tables if missing.
- For quick local testing without Postgres, you can run with TESTING=1 which uses an in‑memory SQLite DB.

### Run (Development)
- With Flask dev server:
  FLASK_APP=app/main.py flask run

- With waitress (prod‑like):
  python app/main.py

The app will be available at http://127.0.0.1:5000.

## Usage
1. Open the app, click Sign Up to create an account.
2. Log in with your credentials.
3. Dashboard: create a new note, edit it, or delete it.
4. Editor: write rich text; changes auto‑save and are versioned.

## API Overview
All API endpoints require the user to be logged in (session cookie).

- GET /api/session — current session user info
- GET /api/notes — list notes for the logged‑in user
- POST /api/notes — create a note (JSON: { title, content })
- GET /api/notes/<id> — fetch a single note
- PUT /api/notes/<id> — update (creates a new active version)
- POST /api/notes/<id>/revert — create a new version from the previous one
- DELETE /api/notes/<id> — delete a note

Legacy endpoint (for backward compatibility):
- POST /save_note — upsert by note_id or title for current user

Example (create note):

curl -X POST http://127.0.0.1:5000/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "New Note", "content": "<p>Body</p>"}' \
  -c cookies.txt -b cookies.txt

Note: Use -c/-b to include the session cookie after logging in via the form.

## Responsiveness
- Viewport meta tags are included in all templates.
- Media queries in CSS adapt layout and typography for tablets and mobiles.
- Fixed asset paths to ensure images load correctly on all devices.

## Database Models and Links
- User: username (unique), email (unique), password_hash
- Note: title, content, user (FK to User), created_at, updated_at, is_active, parent (self‑FK for versioning), version
- UserSession: user (FK to User), session_id (unique), data

Relationships are enforced via ForeignKeyField. Tables are auto‑created at startup if missing. Note.save() updates updated_at to keep timestamps consistent.

## Security
- Passwords are hashed using Werkzeug’s PBKDF2 (generate_password_hash) and stored in the password_hash column. No plaintext passwords are stored.
- CSRF protection is enabled for HTML forms via Flask‑WTF. The signup form includes a CSRF token. JSON API endpoints are CSRF‑exempt and require an authenticated session cookie.
- Secrets and config: the database password is not hard‑coded; provide it via environment (.env). Set a strong SECRET_KEY in production.

## Production Notes
- Set strong SECRET_KEY and secure DB credentials; never expose them.
- Use a managed PostgreSQL instance and psycopg2-binary.
- Consider stricter CORS configuration if hosting a separate frontend.
- Serve behind a proper WSGI server (waitress included here) or your choice.

## Troubleshooting
- “Unauthorized” from API: ensure you are logged in (session cookie present).
- DB connection errors: verify POSTGRES_* env vars and network access.
- Static assets not loading: ensure templates use url_for('static', ...); asset paths inside CSS should be relative to /static (fixed for login background).
