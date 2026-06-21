# MiniLMS — Backend (FastAPI)

The backend of MiniLMS is a RESTful API built with FastAPI. It handles authentication, role-based authorization, core LMS functionality (student, lesson, grade, and transcript management), and a four-module AI capability layer integrated with the OpenRouter Llama 3 gateway.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Auth | OAuth2 + JWT (`python-jose`) |
| Password Hashing | Passlib + bcrypt |
| AI Gateway | OpenRouter (Llama 3) |
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
        ├── lesson_service.py
        └── ai_service.py
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
| `routers/student.py` | Student CRUD, transcript, user management, AI endpoints |
| `routers/lesson.py` | Lesson CRUD, enrollment, unenrollment, student listing |
| `routers/grade.py` | Grade create and update endpoints |
| `services/auth.py` | JWT create/decode, password hash/verify, token extraction |
| `services/logic.py` | Grade range and absenteeism threshold rule helpers |
| `services/lesson_service.py` | Lesson query helpers and success average calculation |
| `services/ai_service.py` | OpenRouter integration; all four AI module implementations |
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

### ✨ AI Operations — `/students`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/students/{id}/comment` | ✨ AI Academic Performance Review | Yes |
| GET | `/students/{id}/recommendations` | ✨ Personalized AI Study Guide | Yes |
| POST | `/students/ai-query` | ✨ NLP-Driven Student Filtering | Yes (teacher/admin) |
| POST | `/students/chat` | ✨ AI Academic Mentor Chatbot | Yes (student only) |

---

## Architecture

```text
Router Layer       →  HTTP endpoints, request/response, authorization guards
Service Layer      →  Shared business logic, domain helpers, AI orchestration
Repository Layer   →  Database interaction and persistence (crud.py)
Model/Schema Layer →  DB entities (models.py) and API contracts (schemas.py)
```

---

## ✨ AI Capability Layer

All four AI modules are implemented in `app/services/ai_service.py` and share a single non-negotiable architectural constraint:

> **The AI layer never accesses the database directly.** Every router fetches data through the existing repository layer (`crud.py`) and passes it into the AI service as plain Python structures. The AI layer receives data, never a session or a query handle.

This constraint is enforced module by module below.

### 1. AI Academic Performance Review

**Function:** `generate_student_comment(transcript_data, student_name)`
**Endpoint:** `GET /students/{id}/comment`

Parses a student's transcript data — already retrieved via `crud.get_student_transcript` — into a structured summary block, then prompts the LLM to evaluate overall academic performance, strengths, and areas for improvement. Output is constrained to a concise narrative report.

### 2. Personalized AI Study Guide

**Function:** `generate_student_recommendations(transcript_data, student_name)`
**Endpoint:** `GET /students/{id}/recommendations`

Operates on the same transcript data contract as the Performance Review module, but applies a distinct risk-analysis pass: lessons with a grade below 60 are flagged as weak, and lessons with absenteeism at or above 3 days are flagged as at-risk. The resulting prompt instructs the model to produce a step-by-step, lesson-specific study plan rather than a general evaluation.

### 3. AI Academic Mentor Chatbot

**Function:** `generate_chatbot_response(user_message, transcript_data, student_name)`
**Endpoint:** `POST /students/chat`

Implements a context-injection pattern. On every chat request:

1. The router resolves the authenticated student strictly from the JWT (`current_user.user_id`) — never from a client-supplied ID.
2. The router fetches that student's transcript through `crud.get_student_transcript`.
3. The transcript is serialized into a ground-truth context block and injected directly into the prompt.
4. The model is instructed to answer exclusively from the supplied context and to decline when the answer is not present in the data, preventing hallucination.

This guarantees per-student data isolation: a student can never receive another student's academic data through the chatbot, by construction of the query rather than by trusting model behavior.

### 4. NLP-Driven Student Filtering

**Function:** `parse_natural_language_query(user_query)`
**Endpoint:** `POST /students/ai-query`

The most security-sensitive module. The LLM never generates SQL. Instead, it is constrained to emit one of four closed JSON schemas (`list_students`, `filter_absenteeism`, `filter_grade`, `unknown`). The router then maps that schema to parameterized SQLAlchemy ORM calls — `.filter()`, `.order_by()`, `func.avg()` — with every value (operator, threshold, limit) validated and whitelisted on the Python side before touching the query builder.

```text
Natural language input
        ↓
LLM constrained to closed JSON schema
        ↓
Backend validates and whitelists every field
        ↓
Parameterized SQLAlchemy ORM query
        ↓
Structured result set
```

No string interpolation, no raw SQL, no path from model output to query execution that bypasses validation. The `limit` field is additionally capped server-side regardless of what the model returns, preventing unbounded result sets from a malformed or adversarial prompt.

---

## Environment Variables

```bash
# Database
export DATABASE_URL="mssql+pyodbc://<user>:<password>@127.0.0.1:1433/<db_name>?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"

# AI Gateway
export OPENROUTER_API_KEY="<your-openrouter-key>"
```

The `OPENROUTER_API_KEY` is loaded via `python-dotenv` at service startup. All four AI functions share a single OpenRouter HTTP client configuration (`_call_openrouter`), so the key, base URL, and model identifier are managed from one location in `ai_service.py`.

---

## Security Model

- Login uses OAuth2 Password Flow via `/auth/login`
- On success, backend returns a signed JWT access token
- Protected endpoints require `Authorization: Bearer <token>`
- Token payload includes `sub` (username), `role`, and `user_id`
- Role checks enforced in all protected routers
- AI endpoints enforce the same role checks as their non-AI counterparts, plus identity-bound data scoping for the chatbot endpoint

---

## Business Rules

### 1. Grade value must be between 0 and 100
Enforced at schema level (Pydantic) and reinforced in `services/logic.py` via `validate_grade_value()`.

### 2. Absenteeism policy (30% threshold)
If absenteeism exceeds 30%, the student automatically fails the lesson. Applied during grade create/update and transcript generation (`Failed (Absenteeism)` status). The same `absenteeism` field feeds the AI Study Guide's at-risk lesson detection.

### 3. Referential integrity
Grade creation requires existing student and lesson records. Student creation requires a valid `user_id`.

### 4. Uniqueness constraints
Student `email` and `student_number` must be unique. Lesson `code` must be unique.

### 5. AI data isolation
AI functions never query the database. All academic data reaches `ai_service.py` exclusively as parameters supplied by router-level calls to `crud.py`.

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

```text
GET /health/db
```

Returns DB connectivity status and startup initialization state.

✓ All four AI endpoints verified against live transcript data
✓ SQL injection surface eliminated in `/students/ai-query` via closed-schema constraint
⚠️ AI endpoints will return a graceful fallback message rather than a 500 error if the OpenRouter gateway is unreachable