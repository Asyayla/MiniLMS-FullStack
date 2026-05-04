# MiniLMS — Full Stack Application

MiniLMS is a Learning Management System built as a full stack monorepo. It provides role-based access for Admins, Teachers, and Students with JWT authentication, lesson/grade management, and transcript generation.

---

## Repository Structure

```text
MiniLMS_Backend/
├── backend/        # FastAPI + SQLAlchemy REST API
└── frontend/       # React + Vite user interface
```

---

## Features

- JWT-based authentication and authorization
- Role-based access control (Admin / Teacher / Student)
- Student management (create, delete, list)
- Lesson management (create, edit, delete)
- Grade entry and update
- Transcript viewing with pass/fail status
- Absenteeism tracking with automatic fail rule (30% threshold)
- Course enrollment and unenrollment

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
| Database Driver | pyodbc (Docker-hosted SQL Server) |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | React (via Vite) |
| Styling | Tailwind CSS |
| HTTP Client | Axios |
| Routing | React Router |

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

API docs available at: `http://127.0.0.1:8000/docs`

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at: `http://localhost:5173`

---

## Database Configuration

The backend uses SQL Server via Docker. The default connection string is configured in `backend/app/database.py`.

To override with an environment variable:

```bash
export DATABASE_URL="mssql+pyodbc://<user>:<password>@127.0.0.1:1433/<db_name>?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
```

---

## Detailed Documentation

- Backend setup, architecture, and API reference: [`backend/README.md`](backend/README.md)
- Frontend setup and page structure: [`frontend/README.md`](frontend/README.md)
