# SDG Assessment Tool — Local Development Setup

This guide gets the app running locally using Docker. Assumes Docker Desktop (or Docker Engine + Compose) is already installed.

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/aikiesan/SDG_Toolbox.git
cd SDG_Toolbox
```

---

## Step 2 — Create the Environment File

```bash
cp .env.example .env
```

The default values in `.env.example` work for local development as-is. No changes needed unless you want custom credentials.

---

## Step 3 — Build and Start Containers

```bash
docker-compose up -d --build
```

This pulls Postgres, builds the Flask app image, and starts both services. First build takes 2–5 minutes. Subsequent starts are fast.

**Verify containers are running:**

```bash
docker-compose ps
```

Both `web` and `db` should show `Up`.

---

## Step 4 — Initialize the Database (First Run Only)

```bash
# Apply schema migrations
docker-compose exec web flask db upgrade

# Seed SDG questions
docker-compose exec web python seed_sdg_questions.py

# Seed strength values
docker-compose exec web python populate_strength_values.py
```

---

## Step 5 — Access the Application

- **Web app:** http://localhost:5000
- **Database (direct):** `localhost:5433` — user: `sdg_user`, password: `sdg_password`, db: `sdg_assessment_dev`

---

## Useful Commands

```bash
# View live logs
docker-compose logs -f web

# Stop containers
docker-compose down

# Stop and wipe database volume (full reset)
docker-compose down -v
```

---

## Troubleshooting

**Port 5000 already in use:**
```bash
# Linux/Mac
lsof -i :5000
# Windows
netstat -ano | findstr :5000
# Kill the conflicting process, or change the port mapping in docker-compose.yml
```

**Database connection error (`password authentication failed`):**
1. Check that `.env` matches the credentials in `docker-compose.yml`
2. Run `docker-compose down && docker-compose up -d`
3. If still broken: `docker-compose down -v && docker-compose up -d --build` (wipes data)

**Code changes not reflected:**
- Python/templates auto-reload — just refresh the browser
- If not: `docker-compose logs -f web` to check for reload errors
- Last resort: `docker-compose up --build`

---

For production deployment on the UIA server, see `UIA_IT_HANDOFF.md`.  
For database schema reference, see `DATABASE_SCHEMA.md`.  
For running the test suite, see `TESTING.md`.
