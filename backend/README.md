# MiniLMS — Backend (FastAPI)

The backend of MiniLMS is a RESTful API built with FastAPI. It provides authentication, role-based authorization, and core LMS functionalities such as student, lesson, grade, and transcript management.

---

## Overview

This service handles all business logic and data persistence for the MiniLMS application.

- JWT-based authentication
- Role-based access control (Admin / Teacher / Student)
- CRUD operations for students and lessons
- Grade management with validation
- Transcript generation
- Absenteeism tracking with automatic fail logic

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

---

## Project Structure

```text
backend/
├── app/
│   ├── api/            # Route definitions (routers)
│   ├── core/           # Security, config, dependencies
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic layer
│   ├── database.py     # DB connection
│   └── main.py         # Application entry point
├── seed_db.py          # Sample data script
├── requirements.txt
└── .env
