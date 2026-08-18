# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Multi-user todo app (TaskFlow) built with Flask + SQLAlchemy, deployed on Railway. See `PLAN.md` for the full architecture diagram and deployment walkthrough.

## Local Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit SECRET_KEY if desired
python app.py           # → http://localhost:5000
```

Uses SQLite locally (`sqlite:///local.db`). In production, Railway injects `DATABASE_URL` pointing to PostgreSQL.

## Key Files

| File | Purpose |
|---|---|
| `app.py` | App factory, DB init, blueprint registration |
| `extensions.py` | Shared `db`, `login_manager`, `bcrypt`, `csrf` instances |
| `models.py` | `User` and `Todo` SQLAlchemy models |
| `routes/auth.py` | `/register` `/login` `/logout` |
| `routes/todos.py` | `/` `/add` `/edit/<id>` `/toggle/<id>` `/delete/<id>` |

## Railway Deployment

1. Push to GitHub; connect repo in Railway dashboard.
2. Add a PostgreSQL plugin — Railway auto-sets `DATABASE_URL`.
3. Set `SECRET_KEY` in Railway → Variables.
4. Railway reads `Procfile` (`web: gunicorn app:app`) and deploys.
5. Tables are created automatically on first boot via `db.create_all()`.

## Patterns to Follow

- All state-changing routes use `POST` (CSRF-protected via `flask-wtf`).
- Every POST form template must include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`.
- `railway postgres://` URLs are rewritten to `postgresql://` in `app.py` before being passed to SQLAlchemy.
- Task ordering is done in Python (`routes/todos.py:_sorted_todos`) for SQLite/PostgreSQL compatibility.
