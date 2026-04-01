# Course Management System — COMP3161

A full-stack course management system built with FastAPI, PostgreSQL, Redis, and React.

**Live API:** https://cmsproject-production-8173.up.railway.app/docs

---

## Prerequisites

Make sure you have the following installed before you begin:

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.10+ | `python3 --version` |
| PostgreSQL | 14+ | `psql --version` |
| Redis | 7+ | `redis-cli --version` |
| Node.js | 18+ | `node --version` |
| Git | any | `git --version` |

---

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/cms_project.git
cd cms_project
```

---

## 2. Set Up PostgreSQL

```bash
# Start PostgreSQL if it isn't running
sudo systemctl start postgresql

# Create the database and user
sudo -u postgres psql <<EOF
CREATE USER cms_user WITH PASSWORD 'cms_password';
CREATE DATABASE cms_db OWNER cms_user;
GRANT ALL PRIVILEGES ON DATABASE cms_db TO cms_user;
EOF
```

---

## 3. Apply the Schema and Views

```bash
psql -h localhost -U cms_user -d cms_db -f sql/create.sql
psql -h localhost -U cms_user -d cms_db -f sql/views.sql
```

---

## 4. Seed the Database

```bash
# Install the seed script dependency
pip install psycopg2-binary

# Run the seed (takes ~5 minutes — inserts 100k students, 200 courses, etc.)
python3 sql/seed.py
```

Expected output at the end:

```
  Account                   100,061 rows
  Student                   100,000 rows
  Course                        200 rows
  Enroll                    450,000+ rows
  ...
✅ Database ready.
```

---

## 5. Set Up the API

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create your `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cms_db
DB_USER=cms_user
DB_PASSWORD=cms_password

JWT_SECRET=your-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## 6. Start Redis

```bash
# Install if needed
sudo apt install -y redis-server

# Start
sudo systemctl start redis

# Verify
redis-cli ping   # should return: PONG
```

---

## 7. Run the API

```bash
uvicorn main:app --reload
```

The API is now running at:
- **API base:** http://localhost:8000
- **Swagger docs:** http://localhost:8000/docs

---

## 8. Set Up and Run the Frontend

```bash
cd frontend
npm install
```

The `frontend/.env` file should already contain:

```env
VITE_API_URL=http://localhost:8000
```

> Change this to the Railway URL if you want to point at the live API instead.

```bash
npm run dev
```

The frontend is now running at **http://localhost:5173**.

---

## Running Both Together (Quick Start)

Open two terminals:

**Terminal 1 — API:**
```bash
cd cms_project
source .venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd cms_project/frontend
npm run dev
```

---

## Running with Docker (Alternative)

If you prefer Docker over manual setup:

```bash
# Build and start everything (API + PostgreSQL + Redis)
docker compose up --build
```

This starts all three services automatically. The API will be at http://localhost:8000.

> Note: You still need to run the seed script manually after the containers start:
> ```bash
> python3 sql/seed.py
> ```

---

## Default Accounts

After seeding, you can register new accounts via the API or frontend.

To create an admin account:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Admin","email":"admin@test.com","password":"admin123","role":"admin"}'
```

---

## Project Structure

```
cms_project/
├── main.py                  # FastAPI entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── api/
│   ├── auth.py              # JWT + password hashing
│   ├── cache.py             # Redis helpers
│   ├── db.py                # psycopg2 connection pool
│   ├── dependencies.py      # FastAPI dependencies + role guards
│   └── routes/
│       ├── auth.py          # Register, login
│       ├── courses.py       # Course CRUD + membership
│       ├── calendar.py      # Calendar events
│       ├── forums.py        # Forums + threads + replies
│       ├── content.py       # Sections + section items
│       ├── assignments.py   # Assignments + submissions + grading
│       └── reports.py       # 5 report views
├── sql/
│   ├── create.sql           # All CREATE TABLE + indexes
│   ├── views.sql            # 5 report views
│   └── seed.py              # Data population script
├── tests/
│   └── test_api.py
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD
└── frontend/
    ├── src/
    │   ├── api.js           # All API calls
    │   ├── App.jsx          # Router
    │   ├── context/
    │   │   └── AuthContext.jsx
    │   ├── components/
    │   │   └── Navbar.jsx
    │   └── pages/
    │       ├── Login.jsx
    │       ├── Register.jsx
    │       ├── Dashboard.jsx
    │       ├── Courses.jsx
    │       ├── CourseDetail.jsx
    │       ├── Forum.jsx
    │       ├── Reports.jsx
    │       └── Admin.jsx
    └── package.json
```

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/courses` | All courses |
| POST | `/courses` | Create course (admin) |
| GET | `/courses/{code}/members` | Course members |
| POST | `/courses/{code}/enroll` | Enroll student |
| GET | `/courses/{code}/content` | Sections + items |
| GET | `/courses/{code}/assignments` | Course assignments |
| POST | `/assignments/{id}/submit` | Submit assignment |
| PUT | `/submissions/{id}/grade` | Grade submission |
| GET | `/courses/{code}/forums` | Course forums |
| GET | `/forums/{id}/threads` | Forum threads |
| POST | `/threads/{id}/reply` | Reply to thread |
| GET | `/reports/top-10-courses` | Top 10 enrolled |
| GET | `/reports/top-10-students` | Top 10 by average |

Full documentation available at `/docs` when the API is running.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI (Python) |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Auth | JWT (python-jose) |
| Frontend | React + Vite + Tailwind CSS |
| Deployment | Railway |
| CI/CD | GitHub Actions |
| Containers | Docker + docker-compose |