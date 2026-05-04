---

## Security Model

- Login uses OAuth2 Password Flow via `/auth/login`
- On success, backend returns a signed JWT access token
- Protected endpoints require `Authorization: Bearer <token>`
- Token payload includes `sub` (username), `role`, and `user_id`
- Role checks enforced in all protected routers

---

## Business Rules

### 1. Grade value must be between 0 and 100
Enforced at schema level (Pydantic) and reinforced in `services/logic.py` via `validate_grade_value()`.

### 2. Absenteeism policy (30% threshold)
If absenteeism exceeds 30%, the student automatically fails the lesson. Implemented via `check_absenteeism_limit()` and applied during grade create/update and transcript generation (`Failed (Absenteeism)` status).

### 3. Referential integrity
Grade creation requires existing student and lesson records. Student creation requires a valid `user_id`.

### 4. Uniqueness constraints
Student `email` and `student_number` must be unique. Lesson `code` must be unique.

---

## Setup and Run

### 1. Enter backend directory

```bash
cd backend
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate environment

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the database (Docker)

```bash
docker start mssql
```

### 6. Run the API

```bash
uvicorn app.main:app --reload
```

Swagger UI: `http://127.0.0.1:8000/docs`

---

## Database Configuration

Default connection string is set in `database.py`. Override with environment variable:

```bash
export DATABASE_URL="mssql+pyodbc://<user>:<password>@127.0.0.1:1433/<db_name>?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
```

---

## Seed Script

Populate sample data for testing:

```bash
python seed_db.py
```

> Note: Requires `kagan` (teacher) and `eda` (student with Student profile) users to exist in the database before running.

---

## Health Check
GET /health/db

Returns DB connectivity status and startup initialization state.
