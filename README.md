# MiNotes

MiNotes is a simple, full‑stack note‑taking application built with Flask (Python) and Peewee ORM, with a minimal Vue front‑end experience for the dashboard and editing. It supports user accounts and CRUD operations for notes.

## Features
- User signup, login, and logout (session‑based)
- Create, read, update, and delete notes
- Rich‑text editing (TipTap) for note content
- Responsive pages for home, login, and signup
- RESTful JSON API consumed by the dashboard

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

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 12+

### Environment Variables
You can override these defaults to point to your own PostgreSQL instance:
- POSTGRES_DB (default: minotes)
- POSTGRES_USER (default: minotes_user)
- POSTGRES_PASSWORD (default provided in code — change in production!)
- POSTGRES_HOST (default: dpg-d212lnmmcj7s73ec1j30-a)
- POSTGRES_PORT (default: 5432)

Create a .env file or export them in your shell before running.

### Setup
1. Create and activate a virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Ensure PostgreSQL is running and credentials are correct (see environment variables above).
4. Initialize the database tables: the app creates tables automatically on import (database.py). On first run, it will print "Database connected and tables created".

### Run (Development)
FLASK_APP=app/main.py flask run

Or run via Python + waitress (as configured in main.py):
python app/main.py

The app will be available at http://127.0.0.1:5000.

## API Overview
All API endpoints require the user to be logged in (session cookie).

- GET /api/session — returns the current session user info
- GET /api/notes — list notes for the logged‑in user
- POST /api/notes — create a note (JSON: { title, content })
- GET /api/notes/<id> — get a single note
- PUT /api/notes/<id> — update a note (JSON: { title, content })
- DELETE /api/notes/<id> — delete a note

Legacy endpoint (for backward compatibility):
- POST /save_note — upsert by note_id or title for current user

Example (create note):

curl -X POST http://127.0.0.1:5000/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "New Note", "content": "<p>Body</p>"}' \
  -c cookies.txt -b cookies.txt

Note: Use -c/-b to include the session cookie after logging in via the form.

## Usage
1. Open the app, click Sign Up to create an account.
2. Log in with your credentials.
3. From the dashboard, create a new note, edit it, or delete it.
4. Use the editor page for rich‑text editing; changes are auto‑saved.

## Responsiveness
- Added viewport meta tags to pages.
- Introduced media queries to adapt layout and typography for tablets and mobiles.

## Database Models
- User: username (unique), email, password
- Note: title, content, user (FK to User), created_at, updated_at, is_active, parent (self‑FK for versioning), version
- UserSession: user (FK to User), session_id (unique), data

Relations are enforced via Peewee ForeignKeyField. Tables are created on startup if missing.

## Production Notes
- Update secret keys and DB credentials. Do not store plaintext passwords in production; use hashing (e.g., bcrypt).
- Configure allowed CORS origins if you host a separate frontend.
- Serve behind a proper WSGI server; waitress is included.

## Troubleshooting
- If you get "Unauthorized" from API endpoints, ensure you are logged in (session cookie present).
- If DB connection errors occur, verify your POSTGRES_* environment variables and network access.
- For static assets not loading, ensure url_for('static', ...) is used in templates (updated in this repo).
