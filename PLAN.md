# TaskFlow — Architecture & Plan

A multi-user todo app built with Flask, deployed on Railway.

---

## Architecture Block Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                 │
│   (Bootstrap 5 HTML pages — rendered by Jinja2 on the server)  │
│                                                                 │
│   /login  /register  /  /add  /edit/<id>  /toggle  /delete     │
└────────────────────┬────────────────────────────────────────────┘
                     │  HTTP request (GET / POST)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RAILWAY CLOUD                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Flask App (Python)                      │  │
│  │                                                          │  │
│  │   app.py          — wires everything together            │  │
│  │   extensions.py   — db, login, bcrypt, csrf             │  │
│  │   models.py       — User, Todo (SQLAlchemy ORM)          │  │
│  │                                                          │  │
│  │   routes/                                                │  │
│  │   ├── auth.py     — /register  /login  /logout           │  │
│  │   └── todos.py    — /  /add  /edit  /toggle  /delete     │  │
│  │                                                          │  │
│  │   templates/                                             │  │
│  │   ├── base.html          — navbar + flash messages       │  │
│  │   ├── auth/login.html                                    │  │
│  │   ├── auth/register.html                                 │  │
│  │   ├── todos/index.html   — dashboard + reminder banner   │  │
│  │   └── todos/edit.html                                    │  │
│  │                                                          │  │
│  │   static/style.css — minor Bootstrap overrides           │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │  SQLAlchemy ORM                    │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │              PostgreSQL Database (Railway plugin)         │  │
│  │                                                          │  │
│  │   users table                todos table                 │  │
│  │   ──────────────             ─────────────────────────   │  │
│  │   id (PK)                    id (PK)                     │  │
│  │   email                      user_id (FK → users.id)     │  │
│  │   password_hash              title                       │  │
│  │   created_at                 notes                       │  │
│  │                              priority (high/med/low)     │  │
│  │                              due_date                    │  │
│  │                              completed                   │  │
│  │                              created_at / updated_at     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Flow (step by step)

```
User clicks "Add Task"
        │
        ▼
Browser sends POST /add  (with form data + CSRF token)
        │
        ▼
Flask receives request → routes/todos.py → add()
        │
        ├─ Validates: title not empty, date format, priority allowed
        ├─ Creates Todo object
        └─ db.session.add() + db.session.commit()  →  PostgreSQL
        │
        ▼
Flask redirects → GET /
        │
        ▼
todos.py → index()
        ├─ Queries all todos for current_user
        ├─ Finds overdue/due-today tasks for reminder banner
        └─ Renders index.html with data
        │
        ▼
Browser shows updated dashboard with reminder banner (if applicable)
```

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Web framework | Flask 3.x | Simple, Railway-native, great docs |
| Database ORM | Flask-SQLAlchemy | Python instead of raw SQL; SQLite locally, PostgreSQL in prod |
| Auth | Flask-Login + Flask-Bcrypt | Session cookies; bcrypt hashes passwords safely |
| CSRF protection | Flask-WTF CSRFProtect | Prevents cross-site request forgery on all POST forms |
| UI | Jinja2 + Bootstrap 5 | Server-rendered HTML, professional look, no JS framework |
| Prod server | Gunicorn | Production-grade WSGI server Railway expects |
| Deployment | Railway | Auto-deploys from git, provides PostgreSQL, sets DATABASE_URL |

---

## File Structure

```
toDo/
├── app.py                  Flask app factory + entry point
├── extensions.py           Shared db / login / bcrypt / csrf instances
├── models.py               User + Todo database models
├── routes/
│   ├── __init__.py
│   ├── auth.py             /register  /login  /logout
│   └── todos.py            /  /add  /edit/<id>  /toggle/<id>  /delete/<id>
├── templates/
│   ├── base.html           Layout, navbar, flash messages
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── todos/
│       ├── index.html      Main dashboard + reminder banner
│       └── edit.html       Edit task form
├── static/
│   └── style.css
├── requirements.txt
├── Procfile                web: gunicorn app:app
├── .env.example            DATABASE_URL + SECRET_KEY template
└── PLAN.md                 ← this file
```

---

## Railway Deployment (step by step)

1. **Push to GitHub** — Railway watches your repo.
2. **Create Railway project** → "Deploy from GitHub repo" → select this repo.
3. **Add PostgreSQL** — in the Railway dashboard, click "+ New" → "Database" → "PostgreSQL".  
   Railway automatically sets the `DATABASE_URL` environment variable in your app.
4. **Set SECRET\_KEY** — in Railway → your service → "Variables" tab → add `SECRET_KEY` with a long random string.
5. **Deploy** — Railway reads `Procfile` (`web: gunicorn app:app`), installs `requirements.txt`, and starts the server.
6. **Tables created automatically** — `app.py` calls `db.create_all()` on first boot, creating all tables.
7. **Visit your Railway URL** — done!

---

## Local Development

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your local env file
cp .env.example .env      # then edit SECRET_KEY if you want

# 4. Run the app
python app.py
# → http://localhost:5000
```

---

## Features

| Feature | How it works |
|---|---|
| Register / Login / Logout | Flask-Login session cookies; bcrypt password hashing |
| Add task | POST /add — title, due date, priority, notes stored in DB |
| Reminder banner | On every page load, queries todos where `due_date ≤ today` and `completed = false` |
| Priority badges | Color-coded: red (High), yellow (Medium), green (Low) |
| Notes / dependencies | Free-text field shown as a tooltip on the task row |
| Edit task | GET/POST /edit/<id> — pre-filled form, saves all fields |
| Mark complete | POST /toggle/<id> — flips `completed` boolean |
| Delete | POST /delete/<id> — removes from DB after confirmation |
| Task ordering | Incomplete first, then sorted by due_date (nulls last) |
| CSRF protection | All POST forms include a hidden `csrf_token` field |

---

---

# Railway — Complete Reference

> Everything you need to know about Railway as a platform, in plain English.

---

## What is Railway?

Railway is an **all-in-one cloud platform** that lets you deploy web apps, background workers, databases, and AI agents without managing servers. You push code to GitHub; Railway builds, deploys, and keeps your app running. It owns its own bare-metal hardware (called **Railway Metal**) in four regions around the world.

Think of it as the gap between "run this on my laptop" and "manage a full AWS account" — Railway handles the infrastructure so you focus on the code.

---

## The Cloud Infrastructure

### Railway Metal (owned hardware)

Railway doesn't just rent servers from AWS or Google — it operates **its own data centres** with bare-metal servers. This is called Railway Metal. The benefits:

- Lower egress cost: **$0.05/GB** (vs $0.10/GB on cloud-rented servers)
- Lower disk cost: **$0.15/GB** (vs $0.25/GB previously)
- Gen 2 sites are interconnected over Railway's own **dark fiber** with 400 Gbps links across 4 redundant paths
- Traffic is routed via Railway's own **anycast Metal Edge network** — meaning requests hit the closest edge node, not a single fixed IP

### Available Regions (as of 2025)

| Region | Location |
|---|---|
| US West Metal | California, USA |
| US East Metal | Virginia, USA |
| EU West Metal | Amsterdam, Netherlands |
| Southeast Asia Metal | Singapore |

All plans (Hobby, Pro, Enterprise) can deploy to any of these four regions. You can also deploy **replicas in multiple regions simultaneously** for high availability.

---

## Supported Languages & Runtimes

Railway uses **Railpack** — its own build system — to auto-detect your stack and build a container image with zero configuration. You just push your code.

**Auto-detected languages:**

| Language | Notes |
|---|---|
| Python | Detects `requirements.txt`, `pyproject.toml`, `Pipfile` |
| Node.js | Detects `package.json`; supports npm, yarn, pnpm |
| Go | Detects `go.mod` |
| Ruby | Detects `Gemfile` |
| Java | Detects `pom.xml` or `build.gradle` |
| PHP | Detects `composer.json` |
| Rust | Detects `Cargo.toml` |
| Elixir | Detects `mix.exs` |
| Deno | Detects `deno.json` |
| Static HTML | Detects a `public/` or `staticfile` folder |
| Shell scripts | Raw shell entrypoints |

**Frameworks** that Railpack understands include Django, Flask, FastAPI, Express, Next.js, NestJS, React (static), Vue, Nuxt, Rails, Laravel, Spring Boot, and many more.

**If Railpack can't detect your stack**, you can:
1. Provide your own `Dockerfile` — Railway will use it directly
2. Deploy a pre-built Docker image from Docker Hub, GHCR, GitLab CR, Microsoft CR, or Quay.io

---

## Databases Supported

Railway offers **one-click database plugins** that inject connection environment variables automatically into your app.

### Built-in templates (zero-config)

| Database | Env var injected | Notes |
|---|---|---|
| **PostgreSQL** | `DATABASE_URL` | Most commonly used; Railway's default DB |
| **MySQL** | `MYSQL_URL` | Full MySQL 8.x support |
| **Redis** | `REDIS_URL` | In-memory cache and message broker |
| **MongoDB** | `MONGO_URL` | Document store |

### Additional databases via Docker / templates

Any open-source database can be deployed using a Docker image or a community template. Examples from the Railway Template Marketplace:

- **ClickHouse** — analytical queries at scale
- **Dragonfly** — Redis-compatible, faster for large datasets
- **MinIO** — S3-compatible object storage
- **ChromaDB** — vector database for AI/embeddings
- **ParadeDB** — Postgres-based with full-text search
- **SurrealDB**, **CockroachDB**, **Cassandra**, and more

### Database browser (built-in)

Railway ships a **visual database view** in the dashboard — you can browse tables, run queries, and inspect data without a separate tool like TablePlus or pgAdmin.

---

## Persistent Storage (Volumes)

By default, Railway services are **stateless** — if a service restarts, any files written to disk are gone. For apps that need to write files and keep them (e.g., SQLite files, user uploads), Railway provides **Volumes**.

```
Your Service ──── mounts at /data ───▶ Volume (persisted disk)
```

Key facts:
- Volumes can be **resized with zero downtime** on all paid plans
- Pro plan: volumes up to **1 TB** self-serve
- Enterprise plan: beyond 1 TB
- Volumes are **region-specific** — the volume lives in the same region as the service
- Cost: **$0.15/GB/month** on Railway Metal

---

## Networking

### Public networking (the internet → your app)

- Every deployed service gets a free **`*.up.railway.app` subdomain** automatically
- You can add your own **custom domain** (e.g., `mytodo.com`) — Railway provisions a **Let's Encrypt SSL certificate** within ~1 hour of your DNS update, auto-renewing every 90 days (ECDSA keys)
- HTTP **request timeout ceiling: 15 minutes** — requests that take longer than this are killed by Railway's edge

### Private networking (service ↔ service)

Services in the same Railway project can talk to each other **without going through the public internet**. This is powered by a **WireGuard mesh VPN** scoped to your project and environment.

```
Flask App  ──[railway.internal]──▶  PostgreSQL
           (encrypted WireGuard, never leaves Railway's network)
```

- Each service gets an internal DNS name: `<service-name>.railway.internal`
- All traffic is encrypted with WireGuard
- Useful for: app → database, app → Redis, microservice → microservice

### TCP Proxy

For services that don't speak HTTP (e.g., a raw game server, a custom protocol), Railway can expose a **TCP proxy** — a public TCP endpoint that routes to your service. Works for both public and internal routing.

### Scaling

- **Vertical scaling**: each service can scale up automatically based on load (memory + CPU)
- **Horizontal scaling**: spin up **multiple replicas** of a service, each running in parallel
- Replicas can be spread across **multiple regions** simultaneously

---

## Pricing Plans

| Plan | Monthly base | Resource credit included | Projects | Max RAM | Max vCPU |
|---|---|---|---|---|---|
| **Free** (trial) | $0 | $5 one-time | 5 | — | — |
| **Hobby** | $5 | $5/month | 50 | 8 GB | 8 |
| **Pro** | $20 | $20/month | 100 | 32 GB | 32 |
| **Enterprise** | Custom | Custom | Unlimited | 48 GB | 64 |

**How billing works:** you pay the base plan fee + actual resource usage. The "resource credit included" offsets usage costs — so a Hobby user on a low-traffic app often pays only the $5/month base.

**Usage rates (Railway Metal):**
- CPU: billed per vCPU-minute
- RAM: billed per GB-minute
- Egress: $0.05/GB
- Disk: $0.15/GB/month

Railway has a **Cost Control** feature (Pro+) where you can set spend caps to avoid surprise bills.

**Compliance:** Railway is **SOC 2 Type II** and **HIPAA** compliant on Enterprise.

---

## Deployment Mechanics

### How a deploy works end-to-end

```
You push to GitHub
        │
        ▼
Railway detects the push (GitHub webhook)
        │
        ▼
Railpack (or your Dockerfile) builds a container image
        │
        ├─ Installs runtime (Python 3.x, Node, etc.)
        ├─ Installs dependencies (pip, npm, etc.)
        └─ Runs build command (if any)
        │
        ▼
Railway pushes image to its internal registry
        │
        ▼
Old container keeps serving traffic
        │
        ▼
New container starts → health check passes
        │
        ▼
Traffic switches to new container (zero-downtime)
        │
        ▼
Old container is stopped
```

### Key deployment features

- **Preview environments** — Railway can spin up a full copy of your app (including its own database) for every pull request. Tear it down when the PR closes.
- **Environment variables** — managed per environment (production, staging, PR preview) in the dashboard or via the CLI. Railway auto-injects database URLs.
- **Config as Code** — you can define your entire Railway project in a `railway.toml` or `railway.json` file committed to your repo (Infrastructure as Code / IaC).
- **Rollbacks** — every deploy is snapshotted; you can one-click roll back to any previous deployment from the dashboard.
- **Cron jobs** — schedule recurring tasks (like a background job) directly in Railway without a separate worker service.
- **Multi-environment** — create isolated `staging`, `production`, `dev` environments in one project, each with their own variables and databases.

---

## MCP Connectivity (AI / Claude Integration)

**MCP (Model Context Protocol)** is a standard that lets AI assistants (like Claude) control external tools and services. Railway has built first-class MCP support.

### What Railway's MCP server can do

An AI agent connected to Railway via MCP can:

**Projects & Services**
- `list_workspaces`, `list_projects`, `create_project`
- `list_services`, `create_service`, `remove_service`
- `connect_service_source` / `disconnect_service_source`
- `get_service_config`, `update_service`, `scale_service`

**Environments & Deployments**
- `create_environment`, `link_environment`, `environment_status`
- `list_deployments`, `deploy` (can be called repeatedly for iterative changes)
- `deploy-template` — deploy any template from Railway's marketplace

**Variables**
- `list_variables`, `set_variables`, `add_reference_variable`

**Domains**
- `generate_domain`, `list_domains`, `domain_status`
- `update_domain`, `delete_domain`, `retry_domain_certificate`

**Logs**
- `get-logs` — fetch build or deployment logs; useful for AI agents debugging a failed deploy

### Two ways to connect

```
┌──────────────────────────────────────────────────────────────────┐
│  Option 1: Local MCP (runs on your machine)                      │
│                                                                  │
│  Claude / Cursor / VS Code                                       │
│       │                                                          │
│       └──▶  Railway CLI  ──▶  Railway API                        │
│            (uses your `railway login` session)                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Option 2: Remote MCP (runs in the cloud)                        │
│                                                                  │
│  Any AI client anywhere                                          │
│       │                                                          │
│       └──▶  mcp.railway.com  ──▶  Railway API                    │
│            (authenticated via OAuth)                             │
│                                                                  │
│  Or: railway mcp proxy (bridges local credentials → Remote MCP)  │
└──────────────────────────────────────────────────────────────────┘
```

### Safety: destructive actions require confirmation

Tools that delete or redeploy things (`remove_service`, `delete_domain`, `redeploy`, `remove_volume`) are **flagged with protocol-level hints** and show a preview before requiring `confirm: true`. This prevents an AI agent from accidentally deleting your database.

### Example: what you can do with Claude + Railway MCP

- Ask Claude to deploy a new service, set its env vars, and generate a public domain — all in one conversation
- Have Claude pull your deployment logs and debug why a service crashed
- Have Claude deploy a Postgres template, link it to your Flask app, and inject the `DATABASE_URL` — zero manual steps

---

## Railway for AI Agents

Railway is increasingly positioned as infrastructure for **always-on AI agents** running in the cloud.

### Sandboxes

Railway **Sandboxes** are ephemeral, isolated Linux environments that an agent (or you) can:
- Spin up on demand via dashboard, CLI, or TypeScript SDK
- Run terminal commands, read/write files, install packages
- Connect to the same private network as your other Railway services (so an agent sandbox can reach your Postgres)
- Snapshot state as a **checkpoint**, then **fork** it into multiple parallel sandboxes
- Tear down cleanly when done

Sandboxes come pre-loaded with **Claude Code, OpenAI Codex, OpenCode, and Pi** — so AI coding agents are ready to run inside them immediately.

### Running autonomous agents

Railway is suited for agents that run **continuously** — monitoring a GitHub repo, processing a queue, responding to webhooks. Example pattern:

```
Railway Service (always-on)
    └─ Monitors GitHub issues
    └─ Creates a branch
    └─ Builds a prompt
    └─ Runs Claude (headless)
    └─ Commits code + opens PR
```

The agent runs as a normal Railway service, billed for the compute it uses, auto-restarted if it crashes.

---

## When Railway CANNOT Be Used (Limitations)

Railway is excellent for most web apps, APIs, background workers, and databases — but it has hard limits. Know these before committing:

### 1. No GPU workloads
Railway does not offer GPU instances. If your app needs a GPU (ML model training, inference, video processing), Railway cannot host it. Use RunPod, Modal, Lambda Labs, or cloud providers with GPU VMs.

### 2. No Bring-Your-Own-Cloud (BYOC)
You cannot deploy Railway's platform into your own AWS/GCP/Azure account. All workloads run on Railway's own infrastructure. If your company policy requires running compute in your own VPC, Railway is not an option.

### 3. No managed Kubernetes
Railway does not expose Kubernetes primitives (pods, deployments, Helm charts, operators). If you need to run a Helm chart or need raw K8s control, use GKE, EKS, or AKS.

### 4. No customer VPC / private cloud networking
You cannot peer your corporate VPC into Railway. Services are isolated within Railway's own private network per-project, but they cannot join your company's private network.

### 5. No multi-cloud
All four regions are Railway's own data centres. You cannot spread workloads across AWS us-east-1 + Railway EU West in a unified deployment. If true multi-cloud redundancy is required, Railway doesn't support it.

### 6. HTTP request timeout: 15 minutes hard ceiling
Any HTTP request that takes longer than 15 minutes is killed. Long-running operations (large file processing, ML batch jobs, video encoding) must be offloaded to background workers or a queue — they cannot run synchronously inside an HTTP handler.

### 7. Volume storage ceiling (without Enterprise)
The self-serve volume limit is **1 TB** on Pro. If your app needs more than 1 TB of persistent disk, you need Enterprise pricing or a separate object storage solution (e.g., S3/R2).

### 8. Four regions only
If your compliance requirements mandate data residency in a country not covered by US (California/Virginia), Netherlands, or Singapore, Railway cannot meet that requirement. No South America, Australia, Middle East, or Africa regions currently exist.

### 9. No SOC 2 / HIPAA on Hobby
Compliance certifications (SOC 2 Type II, HIPAA) are Enterprise-tier only. If you're handling regulated data (healthcare, finance), you need the Enterprise plan.

### 10. Free-tier deploy blackouts
During peak hours in each region, **free-tier deployments are blocked** to protect platform reliability. Hobby, Pro, and Enterprise are unaffected.

### 11. No stateful websocket guarantees across replicas
If you scale a service to multiple replicas and use WebSockets, there is no built-in sticky-session routing. Clients may connect to different replicas on reconnect. You need a pub/sub layer (e.g., Redis) to share state across replicas.

---

## Summary: When to Use Railway vs. Alternatives

| Need | Use Railway? | Alternative |
|---|---|---|
| Deploy a web app / API quickly | ✅ Yes | — |
| Postgres / MySQL / Redis in one click | ✅ Yes | — |
| Multi-user app with auth | ✅ Yes | — |
| Background workers / cron | ✅ Yes | — |
| AI agent hosting (always-on) | ✅ Yes | — |
| Preview environments per PR | ✅ Yes | — |
| Static sites / CDN-only | ⚠️ Partial | Vercel, Cloudflare Pages |
| GPU inference / ML training | ❌ No | RunPod, Modal, Lambda Labs |
| Kubernetes / Helm | ❌ No | GKE, EKS, AKS |
| BYOC / your own VPC | ❌ No | AWS, GCP, Azure |
| >1 TB disk self-serve | ❌ No (need Enterprise) | S3, R2, GCS |
| Data residency outside 4 regions | ❌ No | AWS/GCP regional deployments |
