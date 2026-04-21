# MiniLMS Fullstack (Monorepo)

MiniLMS is a Learning Management System project organized as a monorepo. It currently includes a production-ready FastAPI backend and a frontend workspace prepared for UI development.

## Repository Purpose

This repository is designed to manage core LMS workflows such as:
- User registration and login (JWT-based authentication)
- Student management
- Lesson management
- Grade management and transcript generation
- Academic business rules (grade validation and absenteeism policies)

## Monorepo Structure

```text
MiniLMS_Backend/
├── backend/        # FastAPI + SQLAlchemy backend API
└── frontend/       # Frontend workspace (currently empty / to be implemented)
```

## Backend at a Glance

The backend is built with:
- FastAPI (REST API + Swagger/OpenAPI)
- SQLAlchemy (ORM)
- Pydantic (schema validation)
- JWT (authentication/authorization)
- SQL database connection via `pyodbc` (Docker-based setup, managed with Azure Data Studio)

For full backend technical documentation, setup instructions, architecture, and business rules, see:

- [backend/README.md](backend/README.md)

## Quick Start

### Backend

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open API docs at:
- `http://127.0.0.1:8000/docs`

## Notes

- The backend currently uses database connection settings from `DATABASE_URL` or a default local Docker-compatible connection string.
- Azure Data Studio is used as the database client/management tool.
- The frontend folder is intentionally present for fullstack expansion.
