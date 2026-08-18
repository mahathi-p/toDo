# TaskFlow

A multi-user todo app built with Flask and PostgreSQL, deployed on Railway.

## Features

- Register / login / logout (bcrypt passwords, session cookies)
- Add tasks with due dates, priority (High / Medium / Low), and dependency notes
- Reminder banner on every page load for overdue or due-today tasks
- Edit, complete, and delete tasks
- Color-coded priority badges; task list sorted by incomplete → due date
- CSRF protection on all forms

## Stack

| Layer | Tool |
|---|---|
| Web framework | Flask 3.x (Python) |
| Database | PostgreSQL on Railway (SQLite locally) |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-Login + Flask-Bcrypt |
| UI | Bootstrap 5 + Jinja2 templates |
| Prod server | Gunicorn |

## Local Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optionally edit SECRET_KEY
python app.py                 # → http://localhost:5000
```

## Deploy to Railway

1. Push this repo to GitHub.
2. In Railway dashboard → **New Project** → **Deploy from GitHub repo**.
3. Click **+ New** → **Database** → **PostgreSQL** — Railway injects `DATABASE_URL` automatically.
4. Go to your service → **Variables** → add `SECRET_KEY` (any long random string).
5. Railway reads `Procfile` (`web: gunicorn app:app`), installs `requirements.txt`, and deploys.
6. Database tables are created automatically on first boot.

See [`PLAN.md`](PLAN.md) for the full architecture, Railway platform deep-dive, MCP connectivity guide, and a list of Railway's limitations.
