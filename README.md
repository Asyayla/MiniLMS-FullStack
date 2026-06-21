# MiniLMS — Full Stack Learning Management System

MiniLMS is an enterprise-grade Learning Management System built as a full stack monorepo. It delivers role-based access for Administrators, Teachers, and Students, backed by JWT authentication, complete lesson and grade lifecycle management, automated transcript generation, and a suite of four production AI modules powered by the OpenRouter LLM gateway.

---

## Repository Structure

```text
MiniLMS_Backend/
├── backend/        # FastAPI + SQLAlchemy REST API, AI service layer
└── frontend/       # React 18 + Vite user interface, AI-driven UI modules
```

Each service is independently documented:

- Backend — [`backend/README.md`](backend/README.md)
- Frontend — [`frontend/README.md`](frontend/README.md)

---

## Platform Capabilities

### Core LMS

- JWT-based authentication and role-based authorization (Admin / Teacher / Student)
- Student lifecycle management — creation, lookup, deletion
- Lesson lifecycle management — creation, editing, deletion
- Grade entry and update workflows
- Transcript generation with pass/fail determination
- Absenteeism tracking with an automatic fail rule at the 30% threshold
- Course enrollment and unenrollment

### ✨ AI Capability Layer

MiniLMS embeds four cutting-edge AI modules across the student and faculty experience, all routed through a FastAPI service layer integrated with the OpenRouter Llama 3 gateway. No AI module communicates with the database directly — every model interaction is grounded in data retrieved through the existing service and repository layers, enforcing strict separation between intelligence and persistence.

| Module | Surface | Description |
|--------|---------|-------------|
| ✨ AI Academic Performance Review | `Transcript.jsx` | Automated semantic analysis of a student's grade matrix, producing a structured narrative report on historical academic standing. |
| ✨ Personalized AI Study Guide | `Transcript.jsx` | A data-driven study planner that identifies weak grade thresholds and generates targeted, actionable study recommendations. |
| ✨ AI Academic Mentor Chatbot | `Chatbot.jsx` (global) | A persistent, context-isolated assistant available to authenticated students, answering questions strictly from that student's own academic ledger. |
| ✨ NLP-Driven Student Filtering | `StudentManagement.jsx` | A natural language query gateway for faculty, translating free-text instructor requests into safe, parameterized data filters. |

Full module-level documentation, including prompt architecture and data-isolation guarantees, is provided in the [Backend README](backend/README.md) and [Frontend README](frontend/README.md).

---

## System Architecture

```text
Router Layer        →  HTTP endpoints, request/response contracts, authorization guards
Service Layer        →  Business logic, domain helpers, AI orchestration (ai_service.py)
Repository Layer      →  Database interaction and persistence (crud.py)
Model / Schema Layer   →  DB entities (models.py) and API contracts (schemas.py)
```

The AI service layer sits strictly above the repository layer. It never issues raw SQL or touches the ORM session directly — all academic data is supplied to AI functions as plain Python structures, pre-fetched by routers through `crud.py`. This guarantees that prompt construction, query parsing, and chatbot context injection cannot become a vector for SQL injection or unauthorized data access.

---

## Tech Stack

### Backend

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Auth | OAuth2 + JWT (`python-jose`) |
| Password Hashing | Passlib + bcrypt |
| AI Gateway | OpenRouter (Llama 3) |
| Database Driver | pyodbc (Docker-hosted SQL Server) |

### Frontend

| Layer | Technology |
|-------|-----------|
| Framework | React 18+ (via Vite) |
| Styling | Tailwind CSS |
| HTTP Client | Axios |
| Routing | React Router |
| State Management | Context API |

---

## Quick Start

### 1. Start the Database (Docker)

```bash
docker start mssql
```

If setting up for the first time:

```bash
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourPassword" \
  -p 1433:1433 --name mssql \
  -d mcr.microsoft.com/mssql/server:2022-latest
```

### 2. Start the Backend

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

---

## Database Configuration

The default connection string lives in `backend/app/database.py`. Override it with an environment variable:

```bash
export DATABASE_URL="mssql+pyodbc://<user>:<password>@127.0.0.1:1433/<db_name>?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
```

---

## AI Gateway Configuration

The AI service layer requires an OpenRouter API key, configured at the backend level. See [`backend/README.md`](backend/README.md) for the full environment variable reference and prompt architecture.

```bash
export OPENROUTER_API_KEY="<your-openrouter-key>"
```

---

## Detailed Documentation

- Backend — [`backend/README.md`](backend/README.md)
- Frontend — [`frontend/README.md`](frontend/README.md)

---

## System Status

✓ Core LMS — verified in production
✓ AI Capability Layer (4 modules) — verified in production
✓ Role-based access control — verified in production
⚠️ SQL Server must be running and reachable before backend startup, or the API will fail health checks at `/health/db`.
