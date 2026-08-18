# Things to Do

A multi-user todo app built with Flask and PostgreSQL, deployed on Railway.

## Features

- Register / login / logout (bcrypt passwords, session cookies)
- Add tasks with due dates, priority (High / Medium / Low), category, and dependency notes
- Group and filter tasks by category
- Reminder banner on every page load for overdue or due-today tasks
- Edit, complete, and delete tasks
- Sticky-note UI with colour-coded priorities; tasks sorted by incomplete → due date
- CSRF protection on all forms

## Stack

| Layer | Tool |
|---|---|
| Web framework | Flask 3.x (Python) |
| Database | PostgreSQL on Railway (SQLite locally) |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-Login + Flask-Bcrypt |
| UI | Bootstrap 5 + Jinja2 templates + Google Fonts |
| Prod server | Gunicorn |

---

## Local Development

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up local environment variables
cp .env.example .env        # optionally change SECRET_KEY

# 4. Run the app
python app.py               # → http://localhost:5000
```

Your local database is created automatically at `instance/local.db` (SQLite) the first time the app starts.

---

## Deploy to Railway (first time)

### Step 1 — Push your code to GitHub

```bash
git add .
git commit -m "initial commit"
git push origin main
```

### Step 2 — Create a Railway project

1. Go to [railway.com](https://railway.com) and sign in.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select your `toDo` repository. Railway immediately starts building.

### Step 3 — Add a PostgreSQL database

1. Inside your Railway project, click **+ New** → **Database** → **PostgreSQL**.
2. Railway automatically creates a `DATABASE_URL` environment variable and injects it into your app. No extra configuration needed.

### Step 4 — Set your SECRET_KEY

1. Click your Flask service (not the database) in the Railway dashboard.
2. Go to the **Variables** tab.
3. Add a new variable:
   ```
   SECRET_KEY = (a long random string — generate one with: openssl rand -hex 32)
   ```

### Step 5 — Watch it deploy

Railway reads your `Procfile` (`web: gunicorn app:app`), installs `requirements.txt`, and starts the server. Watch progress in the **Deployments** tab. When the status shows **Active**, your app is live.

Database tables (`user`, `todo`) are created automatically on the first boot — no migration step needed.

### Step 6 — Get your public URL

1. Click your Flask service → **Settings** tab → **Networking** section.
2. Click **Generate Domain**. You'll get a URL like:
   ```
   https://todo-production-a3f8.up.railway.app
   ```
3. Open that URL in any browser — your app is live on the internet.

---

## Updating after the first deploy

Every push to `main` triggers an automatic redeploy:

```bash
git add .
git commit -m "describe your change"
git push origin main
```

Railway detects the push, rebuilds the container, and swaps it in with zero downtime.

---

## Important notes

- **Local data does not carry over.** Your `instance/local.db` (SQLite) is only used on your machine. The Railway PostgreSQL database starts empty — you'll need to register a new account on the live URL.
- **SECRET_KEY must stay secret.** It signs session cookies and CSRF tokens. If someone knows it, they can forge logins. Never commit it to Git.
- **Free-tier deploys may be delayed during peak hours** on Railway's free plan. Hobby ($5/mo) and above are unaffected.

---

See [`PLAN.md`](PLAN.md) for the full architecture diagram, Railway platform deep-dive, MCP connectivity guide, and a list of Railway's limitations.

---

## Auto-deployment on Railway

There are three ways to automate the entire Railway setup — from creating the project to getting a live URL — without clicking through the dashboard manually.

---

### Option 1 — Git push (always-on, zero effort)

This is the default Railway behaviour once the project is set up. Every push to `main` triggers a full redeploy automatically.

**Steps:**
1. Complete the first-time setup (Steps 1–6 above) once.
2. After that, every `git push origin main` is all you ever do.

**How it works under the hood:**
```
git push → GitHub webhook → Railway detects change
       → Railpack builds container → health check passes
       → new container goes live → old one is stopped
```

**Deploy time:** 1–3 minutes for a Python app this size.

**Pros:**
- Zero extra tooling — just Git
- Zero-downtime swap (old container stays live until new one is healthy)
- Automatic rollback available in the dashboard if something breaks
- Works from any machine, any OS

**Cons:**
- First-time project/database setup still requires clicking through the dashboard (unless you use Option 2 or 3)
- No control over when the deploy happens — every push deploys, even typo fixes

---

### Option 2 — Railway CLI script (automate first-time setup)

The Railway CLI lets you create projects, add databases, set variables, and deploy — all from your terminal. The script at `scripts/railway_setup.sh` does the full first-time setup in one command.

**Steps:**
```bash
# 1. Install the Railway CLI (one time)
npm install -g @railway/cli

# 2. Run the setup script from your project root
bash scripts/railway_setup.sh
```

The script handles: login → create project → add PostgreSQL → set SECRET_KEY → link DATABASE_URL → deploy → generate domain.

**After that**, Option 1 (git push) takes over for all future deploys.

**Deploy time:** Same 1–3 minutes; the script just eliminates the dashboard clicks.

**Pros:**
- Entire first-time setup in one command (~2 minutes)
- Repeatable — run it again for staging environments or new projects
- Scriptable inside CI/CD pipelines (GitHub Actions, etc.)
- No browser required after initial `railway login`

**Cons:**
- Requires Node.js installed (for `npm install -g @railway/cli`)
- First run opens a browser for `railway login` (one-time OAuth)
- CLI commands can change between Railway CLI versions

---

### Option 3 — Railway MCP (let Claude do it in plain English)

Railway has a built-in MCP (Model Context Protocol) server. Once connected to Claude Code, you can describe what you want in plain English and Claude controls Railway directly — creating services, setting variables, reading logs, and deploying — with no manual steps.

**Steps (one-time setup):**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Add Railway MCP to Claude Code settings
# Edit: ~/.claude/settings.json
```

Add this to your Claude Code `settings.json`:

```json
{
  "mcpServers": {
    "railway": {
      "command": "railway",
      "args": ["mcp"]
    }
  }
}
```

Restart Claude Code. Then in any session, just ask:

> *"Deploy my app to Railway, add a Postgres database, set a random secret key, and give me the live URL."*

Claude will call Railway's API tools (`create_project`, `create_service`, `set_variables`, `generate_domain`, `get_logs`, etc.) and handle everything.

**Deploy time:** Same 1–3 minutes for the build; the MCP setup conversation takes about 30 seconds.

**Pros:**
- No dashboard clicks, no script writing — plain English instructions
- Claude can also read your deployment logs and debug failures automatically
- Works for complex setups (multiple services, staging environments, cron jobs)
- Remote MCP option (`mcp.railway.com`) works from anywhere, not just your laptop

**Cons:**
- Requires Railway CLI installed and logged in
- Destructive actions (delete service, remove database) need explicit confirmation — review what Claude is about to do before approving
- MCP session uses your Railway account permissions — treat it like giving Claude your dashboard access

---

### Which clouds does Railway support?

Railway runs on its **own hardware** (not AWS, GCP, or Azure). It operates four regions:

| Region | Location |
|---|---|
| US West | California, USA |
| US East | Virginia, USA |
| EU West | Amsterdam, Netherlands |
| SE Asia | Singapore |

**What this means for you:**
- You cannot deploy to AWS us-east-1 or Google Cloud specifically — Railway is its own cloud
- You pick one of the four regions when creating a service (or Railway picks US West by default)
- For multi-region deployments, Railway can run replicas of your service in multiple regions simultaneously (Pro plan)

---

### Approximate cost

| Scenario | Monthly cost |
|---|---|
| Personal project, low traffic | **~$5** (Hobby plan, usage stays within the included credit) |
| Small team, moderate traffic | **~$20** (Pro plan) |
| High traffic / large DB | **$20 + usage overages** (Pro + resource billing) |

**How the billing works:**
- You pay the plan fee ($5 Hobby / $20 Pro) plus actual resource usage (CPU, RAM, egress, disk)
- Each plan includes a credit equal to the plan fee that offsets usage
- A small app like this todo app will almost never exceed the included credit on Hobby

**To avoid surprise bills:** Railway → your account → Usage → set a **spend limit** cap.

---

### How fast are deploys?

| Stage | Time |
|---|---|
| Railway detects your git push | < 5 seconds |
| Railpack builds the container | 60–90 seconds (first build); 20–40s after (cached layers) |
| Container starts + health check | 5–15 seconds |
| **Total: code pushed → live** | **~2 minutes** |

Zero downtime — the old version keeps serving traffic until the new one is healthy.

---

### How large an app can be deployed?

Railway handles apps ranging from a simple todo app to production SaaS products. The practical limits per plan:

| Limit | Hobby | Pro | Enterprise |
|---|---|---|---|
| RAM per service | 8 GB | 32 GB | 48 GB |
| CPU per service | 8 vCPU | 32 vCPU | 64 vCPU |
| Persistent disk | 5 GB (default) | Up to 1 TB | Beyond 1 TB |
| Services per project | 50 | 100 | Unlimited |
| Concurrent replicas | Multiple | Multiple | Multiple |
| HTTP request timeout | 15 min | 15 min | 15 min |

**What Railway handles well:**
- Web apps, REST APIs, GraphQL APIs
- Background workers and cron jobs
- PostgreSQL, MySQL, Redis, MongoDB databases
- WebSocket servers (with Redis for multi-replica state)
- AI agents and always-on automation services

**What Railway cannot do (hard limits, any plan):**
- GPU workloads (no GPU instances available)
- HTTP requests longer than 15 minutes (use background workers instead)
- Bring-your-own-cloud / deploy into your own AWS or GCP VPC
- Data residency outside the 4 available regions
- Managed Kubernetes / Helm charts
