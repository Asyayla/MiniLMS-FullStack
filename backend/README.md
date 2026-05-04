# MiniLMS Backend

FastAPI-based backend service for the MiniLMS platform.

This service provides authentication, student/lesson/grade management, and transcript generation with domain-specific academic rules.

---

## Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Auth:** OAuth2 Password Flow + JWT (`python-jose`)
- **Password Hashing:** Passlib + bcrypt
- **Database Driver:** `pyodbc` (Docker-hosted database connection)
- **DB Client Tool:** Azure Data Studio

---

## Backend Folder Structure (File-by-File)

```text
backend/
├── .gitignore
├── .idea/
├── .venv/
├── README.md
├── requirements.txt
├── seed_db.py
└── app/
		├── main.py
		├── database.py
		├── models.py
		├── schemas.py
		├── crud.py
		├── routers/
		│   ├── auth.py
		│   ├── student.py
		│   ├── lesson.py
		│   └── grade.py
		└── services/
				├── auth.py
				├── logic.py
				└── lesson_service.py
```

### Root-level files

- **.gitignore**: Excludes local/dev artifacts from version control.
- **.idea/**: IDE metadata (PyCharm/JetBrains).
- **.venv/**: Project-local Python virtual environment.
- **README.md**: This technical backend documentation.
- **requirements.txt**: Python dependencies with pinned versions.
- **seed_db.py**: Seeds demo/test records (teacher, lesson, many students/grades) for testing.

### `app/` application layer

- **main.py**
	- FastAPI app bootstrap.
	- Registers routers.
	- Defines OpenAPI tag order.
	- Startup DB initialization and DB health endpoint.

- **database.py**
	- SQLAlchemy engine/session/base configuration.
	- `DATABASE_URL` support with Docker-compatible default fallback.
	- DB connection health checks.
	- Optional auto-create database behavior.

- **models.py**
	- SQLAlchemy entities: `User`, `Student`, `Lesson`, `Grade`.
	- Relationship mapping and FK structure.

- **schemas.py**
	- Pydantic request/response models.
	- Email format validation (`EmailStr`).
	- Grade range constraints (0–100) and absenteeism lower bound.

- **crud.py**
	- Repository-level DB operations.
	- Enforces business rules through `services.logic`.
	- Handles integrity errors and maps them to API-friendly HTTP errors.

### `app/routers/`

- **auth.py**
	- `/auth/register` and `/auth/login` endpoints.
	- Returns JWT for authenticated clients.

- **student.py**
	- `/students/` create/read endpoints.
	- `/students/{id}/transcript` for transcript output.

- **lesson.py**
	- `/lessons/` create endpoint (role-protected).
	- Lesson detail and success statistics endpoints.

- **grade.py**
	- `/grades/` create and update endpoints.
	- Role-protected (`teacher` / `admin`).

### `app/services/`

- **auth.py**
	- JWT create/decode utilities.
	- Password hash/verify functions.
	- Current-user extraction from bearer token.

- **logic.py**
	- Domain business-rule helpers.
	- Grade range checks and absenteeism threshold checks.

- **lesson_service.py**
	- Lesson query helper methods.
	- Lesson-level success average calculation.

---

## API Modules and Route Prefixes

- **Entry Operations**: `/auth/*`
- **Student Operations**: `/students/*`
- **Lesson Operations**: `/lessons/*`
- **Grade Operations**: `/grades/*`

Swagger UI: `http://127.0.0.1:8000/docs`

---

## Layered Architecture

The project follows a practical layered approach:

1. **Router Layer** (`app/routers/*`)
	 - HTTP endpoints, request/response boundaries, authorization guards.

2. **Service Layer** (`app/services/*`)
	 - Shared business/domain logic and helper functions.

3. **Repository Layer** (`app/crud.py`)
	 - Database interaction and persistence logic.

4. **Model/Schema Layer** (`models.py`, `schemas.py`)
	 - Data representation in DB and API contracts.

---

## Security Model (JWT)

- Login uses OAuth2 Password flow through `/auth/login`.
- On successful authentication, backend returns a JWT access token.
- Protected endpoints require `Authorization: Bearer <token>`.
- Token payload includes:
	- `sub` (username)
	- `role` (`admin` / `teacher` / `student`)
- Role checks are enforced in protected routers (e.g., grade and lesson creation).

---

## Business Rules (Technical)

### 1) Grade value must be between 0 and 100

- Enforced at schema level (`GradeCreate`, `GradeUpdate`) with Pydantic constraints.
- Reinforced at service/repository level with `validate_grade_value()`.

### 2) Absenteeism policy (30% threshold)

- Rule: if absenteeism exceeds 30%, student is considered failed for the lesson.
- Implemented with `check_absenteeism_limit()` and applied in:
	- Grade create/update validations.
	- Transcript status computation (`Failed (Absenteeism)`).

### 3) Referential integrity checks

- Grade creation requires existing student and lesson records.
- Student creation requires existing `user_id`.

### 4) Uniqueness constraints

- Student `email` and `student_number` are validated to avoid duplicates.
- Lesson `code` is validated as unique.

---

## Setup and Run

### 1) Enter backend directory

```bash
cd backend
```

### 2) Create virtual environment (if needed)

```bash
python3 -m venv .venv
```

### 3) Activate environment

```bash
source .venv/bin/activate
```

### 4) Install dependencies

```bash
pip install -r requirements.txt
```

### 5) Run API

```bash
uvicorn app.main:app --reload
```

If `--reload` is unstable in your environment, run without reload:

```bash
uvicorn app.main:app
```

---

## Database Configuration

By default, `database.py` uses a Docker-compatible database connection string.

Recommended: override with environment variable.

```bash
export DATABASE_URL="mssql+pyodbc://<user>:<password>@127.0.0.1:1433/<db_name>?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
```

You can manage and inspect the running database with **Azure Data Studio**.

---

## Seed Script

Populate sample data:

```bash
python seed_db.py
```

The script inserts sample users, one lesson, and a large student/grade dataset for development/testing.

---

## Health Check

- `GET /health/db` returns DB connectivity and startup-init status.

---

## Notes

- This backend is the API part of the `minilms-fullstack` repository.
- Frontend integration can consume this service directly via REST.
