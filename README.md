# TaskFlow — Task Management App
> Hairdrama Tech Internship Assignment

A full-stack collaborative task management application with Google OAuth, real-time updates, and Gmail email notifications.

**Live URLs** *(update after deployment)*
- Frontend: `https://taskflow.vercel.app`
- Backend API: `https://taskflow-api.railway.app`

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       USER / BROWSER                         │
└─────────────┬──────────────────────────┬─────────────────────┘
              │ HTTPS                    │ OAuth redirect
              ▼                          ▼
┌─────────────────────────┐  ┌─────────────────────────────┐
│  FRONTEND (Vercel)      │  │  Google OAuth 2.0           │
│  Next.js 14 + TypeScript│  │  accounts.google.com        │
│  App Router · Tailwind  │  └─────────────────────────────┘
│  /login                 │
│  /dashboard (Kanban)    │
│  /tasks/[id]            │
└─────────────┬───────────┘
              │ REST + JWT Bearer token
              ▼
┌─────────────────────────┐  ┌─────────────────────────────┐
│  BACKEND (Railway)      │  │  Supabase                   │
│  Flask 3 · Python 3.11  │──│  PostgreSQL + RLS           │
│  /auth/google           │  │  users · tasks              │
│  /auth/callback         │  │  task_assignments           │
│  /tasks  (CRUD)         │  │  Realtime websockets        │
│  /users                 │  └─────────────────────────────┘
│  Email notification svc │
└─────────────┬───────────┘
              │ Gmail API (service account)
              ▼
┌─────────────────────────────┐
│  Gmail API                  │
│  Task assigned → assignee   │
│  Task done → creator        │
└─────────────────────────────┘
```

**Request flow (create task):**
1. User fills form in Next.js → `POST /tasks` with JWT
2. Flask validates JWT, inserts row in Supabase
3. Flask spawns background thread → Gmail API sends notification
4. Response returns to frontend, dashboard re-fetches tasks

---

## Tech Stack

| Layer | Technology | Hosting |
|---|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS | Vercel |
| Backend | Flask 3, Python 3.11, Authlib, PyJWT | Railway / Render |
| Database | Supabase (PostgreSQL + RLS) | Supabase |
| Auth | Google OAuth 2.0 | Google Cloud |
| Email | Gmail API (service account) | Google Cloud |
| Migrations | Plain SQL files in `/migrations` | — |

---

## Features

- Google OAuth 2.0 login (no passwords)
- Kanban board: To do / In progress / Done columns
- Create tasks with title, description, priority, due date
- Assign tasks to any registered user
- Email notifications: assigned (to assignee) + completed (to creator)
- Task detail view with edit and delete
- Search and priority filter
- JWT-based stateless auth

---

## Project Structure

```
taskflow/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory + CORS
│   │   ├── db.py                # Supabase client singleton
│   │   ├── email_service.py     # Gmail API + HTML email templates
│   │   ├── auth/
│   │   │   ├── middleware.py    # @require_auth JWT decorator
│   │   │   └── routes.py        # /auth/google, /callback, /me
│   │   ├── tasks/
│   │   │   └── routes.py        # GET/POST/PATCH/DELETE /tasks
│   │   └── users/
│   │       └── routes.py        # GET /users
│   ├── migrations/
│   │   ├── 001_create_users.sql
│   │   ├── 002_create_tasks.sql
│   │   └── 003_create_task_assignments.sql
│   ├── .env.example
│   ├── Procfile                 # gunicorn for Railway/Render
│   ├── requirements.txt
│   └── run.py
│
└── frontend/
    ├── app/
    │   ├── layout.tsx           # Root layout + AuthProvider
    │   ├── globals.css
    │   ├── page.tsx             # Root redirect
    │   ├── login/page.tsx       # Login page
    │   ├── auth/callback/page.tsx # JWT capture after OAuth
    │   ├── dashboard/page.tsx   # Kanban board
    │   └── tasks/[id]/page.tsx  # Task detail
    ├── components/
    │   ├── Navbar.tsx
    │   ├── TaskCard.tsx
    │   └── TaskForm.tsx         # Create/edit modal
    ├── lib/
    │   ├── api.ts               # fetch wrappers (GET/POST/PATCH/DELETE)
    │   ├── auth-context.tsx     # AuthContext + JWT storage
    │   └── utils.ts             # cn, formatDate, priorityConfig, etc.
    ├── types/index.ts           # TypeScript interfaces
    ├── .env.local.example
    └── package.json
```

---

## Database Schema

### `users`
```sql
id          UUID PRIMARY KEY
email       TEXT UNIQUE NOT NULL
name        TEXT
avatar_url  TEXT
google_id   TEXT UNIQUE NOT NULL
created_at  TIMESTAMPTZ
```

### `tasks`
```sql
id           UUID PRIMARY KEY
title        TEXT NOT NULL
description  TEXT
status       ENUM('todo','in_progress','done')
priority     ENUM('low','medium','high')
due_date     DATE
creator_id   UUID → users(id)
assignee_id  UUID → users(id)
created_at   TIMESTAMPTZ
updated_at   TIMESTAMPTZ
```

### `task_assignments` *(audit log)*
```sql
id          UUID PRIMARY KEY
task_id     UUID → tasks(id)
assigned_to UUID → users(id)
assigned_by UUID → users(id)
assigned_at TIMESTAMPTZ
```

---

## API Endpoints

### Auth
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/auth/google` | — | Redirect to Google consent |
| GET | `/auth/callback` | — | Exchange code, return JWT |
| GET | `/auth/me` | ✓ | Current user profile |
| POST | `/auth/logout` | — | Clear session |

### Tasks
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/tasks` | ✓ | List user's tasks |
| POST | `/tasks` | ✓ | Create task |
| GET | `/tasks/:id` | ✓ | Get task |
| PATCH | `/tasks/:id` | ✓ | Update task |
| DELETE | `/tasks/:id` | ✓ | Delete task (creator only) |

### Users
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/users` | ✓ | All users (assignee picker) |
| GET | `/users/:id` | ✓ | Single user |

---

## Setup & Local Development

### Prerequisites
- Python 3.11+, Node.js 20+
- [Supabase](https://supabase.com) project (free tier)
- [Google Cloud](https://console.cloud.google.com) project with OAuth + Gmail API

### 1. Clone
```bash
git clone https://github.com/your-username/taskflow.git
cd taskflow
```

### 2. Database — run migrations in order
In Supabase SQL Editor, paste and run each migration file:
```
backend/migrations/001_create_users.sql
backend/migrations/002_create_tasks.sql
backend/migrations/003_create_task_assignments.sql
```

### 3. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # fill in all values
flask run --port 5000
```

### 4. Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local  # fill in values
npm run dev
```

Visit `http://localhost:3000`.

---

## Environment Variables

### `backend/.env.example`
```env
FLASK_SECRET_KEY=change-me-to-a-random-secret
FLASK_ENV=development
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback
JWT_SECRET=change-me-to-a-random-jwt-secret
JWT_EXPIRY_HOURS=24
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
GMAIL_CREDENTIALS_PATH=gmail_credentials.json
GMAIL_SENDER_EMAIL=noreply@yourdomain.com
FRONTEND_URL=http://localhost:3000
```

### `frontend/.env.local.example`
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## Deployment

### Supabase
1. Create project → run migrations in SQL Editor
2. Copy Project URL + Service Role Key

### Backend → Railway
1. Push `backend/` to GitHub
2. New Railway project → Deploy from GitHub repo → root: `backend/`
3. Set all env vars from `.env.example`
4. Railway detects Python; `Procfile` runs gunicorn
5. Note the generated URL

### Frontend → Vercel
1. Import repo on [vercel.com](https://vercel.com)
2. Root Directory: `frontend`
3. Set `NEXT_PUBLIC_API_URL` to your Railway URL
4. Deploy — auto-deploys on every push to `main`

### Google Cloud setup
1. Create project → enable **Gmail API** + **Google+ API**
2. Credentials → OAuth 2.0 → Web application
3. Authorized redirect URIs:
   - `http://localhost:5000/auth/callback`
   - `https://your-railway-app.railway.app/auth/callback`
4. For Gmail: create a Service Account → enable domain-wide delegation
5. Download JSON → save as `backend/gmail_credentials.json` (never commit)

---

## Commit History Guidelines

This repo uses conventional commits:

```bash
git commit -m "feat: add Google OAuth login flow"
git commit -m "feat: create tasks CRUD API"
git commit -m "feat: assign tasks with email notification"
git commit -m "feat: kanban board with status columns"
git commit -m "feat: task detail page with edit/delete"
git commit -m "fix: JWT expiry not invalidating correctly"
git commit -m "chore: add migrations and .env.example"
git commit -m "docs: complete README with architecture"
git commit -m "deploy: configure Procfile for Railway"
```

---

## Key Design Decisions

**Why our own JWT instead of Supabase Auth?**
Supabase Auth is session-based. Flask stays stateless by issuing its own HS256 JWT on OAuth callback. The service-role key (used backend-only) bypasses RLS for server writes while keeping the frontend fully unauthenticated.

**Why background threads for email?**
Gmail API calls can take 1–2 s. `threading.Thread(daemon=True)` lets the API return immediately while email sends in the background — no task queue infrastructure required for this scale.

**Gmail API scopes:**
Only `gmail.send` — write-only. The app never reads users' inboxes.
