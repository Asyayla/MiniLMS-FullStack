# MiniLMS — Backend (FastAPI)

The backend of MiniLMS is a RESTful API built with FastAPI. It handles authentication, role-based authorization, and core LMS functionalities including student, lesson, grade, and transcript management.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Auth | OAuth2 + JWT (`python-jose`) |
| Password Hashing | Passlib + bcrypt |
| Database | SQL Server (Docker) |
| Driver | pyodbc |
| DB Client | Azure Data Studio |

---

## Project Structure

```text
backend/
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

### File Descriptions

| File | Description |
|------|-------------|
| `main.py` | App bootstrap, router registration, DB health endpoint |
| `database.py` | SQLAlchemy engine/session config, connection health checks |
| `models.py` | `User`, `Student`, `Lesson`, `Grade` entities and relationships |
| `schemas.py` | Pydantic request/response models and validation constraints |
| `crud.py` | Repository-level DB operations and business rule enforcement |
| `routers/auth.py` | Register, login, change-password endpoints |
| `routers/student.py` | Student CRUD, transcript, user management endpoints |
| `routers/lesson.py` | Lesson CRUD, enrollment, unenrollment, student listing |
| `routers/grade.py` | Grade create and update endpoints |
| `services/auth.py` | JWT create/decode, password hash/verify, token extraction |
| `services/logic.py` | Grade range and absenteeism threshold rule helpers |
| `services/lesson_service.py` | Lesson query helpers and success average calculation |
| `seed_db.py` | Seeds demo data for development and testing |

---

## API Reference

### Authentication — `/auth`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and receive JWT token | No |
| PUT | `/auth/change-password` | Change current user's password | Yes |

### Student Operations — `/students`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/students/` | Create a new student profile | Yes |
| GET | `/students/` | List all students | Yes |
| GET | `/students/{id}` | Get student by ID | Yes |
| GET | `/students/{id}/transcript` | Get student transcript | Yes |
| GET | `/students/users/all` | List all system users (admin only) | Yes |
| PUT | `/students/users/{id}` | Update user role (admin only) | Yes |
| DELETE | `/students/users/{id}` | Delete user (admin only) | Yes |

### Lesson Operations — `/lessons`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/lessons/` | Create a new lesson | Yes (teacher/admin) |
| GET | `/lessons/` | List lessons (filtered by role) | Yes |
| GET | `/lessons/{id}` | Get lesson details | Yes |
| PUT | `/lessons/{id}` | Update lesson (admin only) | Yes |
| DELETE | `/lessons/{id}` | Delete lesson (admin only) | Yes |
| POST | `/lessons/{id}/enroll` | Enroll in a lesson (student only) | Yes |
| DELETE | `/lessons/{id}/enroll` | Unenroll from a lesson (student only) | Yes |
| GET | `/lessons/{id}/students` | List enrolled students (teacher/admin) | Yes |

### Grade Operations — `/grades`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/grades/` | Submit a grade | Yes (teacher/admin) |
| PUT | `/grades/{id}` | Update a grade | Yes (teacher/admin) |

---

## Architecture
Router Layer       →  HTTP endpoints, request/response, authorization guards
Service Layer      →  Shared business logic and domain helpers
Repository Layer   →  Database interaction and persistence (crud.py)
Model/Schema Layer →  DB entities (models.py) and API contracts (schemas.py)

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
If absenteeism exceeds 30%, the student automatically fails the lesson. Applied during grade create/update and transcript generation (`Failed (Absenteeism)` status).

### 3. Referential integrity
Grade creation requires existing student and lesson records. Student creation requires a valid `user_id`.

### 4. Uniqueness constraints
Student `email` and `student_number` must be unique. Lesson `code` must be unique.

---

## Setup and Run

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker start mssql
uvicorn app.main:app --reload
```

Swagger UI: `http://127.0.0.1:8000/docs`

---

## Database Configuration

```bash
export DATABASE_URL="mssql+pyodbc://<user>:<password>@127.0.0.1:1433/<db_name>?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
```

---

## Seed Script

```bash
python seed_db.py
```

> Requires `kagan` (teacher) and `eda` (student with Student profile) users to exist before running.

---

## Health Check

GET /health/db
Returns DB connectivity status and startup initialization state.
