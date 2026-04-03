# Startup Incubator Full Stack

React frontend + Flask backend + MySQL-ready persistence for the startup incubator system.

## Structure

- `backend/` Flask API with SQLAlchemy models, JWT auth, and role-based routes
- `frontend/` React SPA built with Vite
- `schema.sql` relational baseline from the requirements
- `requirements-traceability.md` mapping from F1-F17 to implementation scope
- `software-requirements-specification.md` formal SRS document for the project

## Backend setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update MySQL credentials.
4. Create the database in MySQL:

```sql
CREATE DATABASE incubator_db;
```

5. Initialize tables and seed initial roles and users:

```bash
python seed.py
```

6. Run the Flask server:

```bash
python run.py
```

API base URL: `http://localhost:5000/api`

Seeded accounts:
- `admin@example.com` / `Admin@123`
- `mentor@example.com` / `Mentor@123`

## Frontend setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Optional environment file:

```bash
echo VITE_API_URL=http://localhost:5000/api > .env
```

3. Start the UI:

```bash
npm run dev
```

Frontend URL: `http://localhost:5173`

## Automated tests

Backend API tests are in `backend/tests/`.

Run them with:

```bash
cd backend
python -m pytest tests -q
```

## Implemented baseline

- Registration for startup representatives and investors
- Login with JWT-based role claims
- Role-guarded startup CRUD
- Investor startup directory and express-interest flow
- Mentor assignment and session endpoints
- Admin progress report and audit log endpoints
- React dashboard with role-aware panels
- Funding-round create and update APIs plus admin UI
- Startup-representative views for milestones, mentors, and funding history
- Search across startups and users
- Pytest-based backend API tests

## Gaps to build next

- Funding round create and update UI
- Startup representative self-service views
- Search across investors and mentors
- Database migrations
- Automated tests
