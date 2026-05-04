# MiniLMS — Frontend (React + Vite)

The frontend of MiniLMS is a modern single-page application built with React and Vite. It provides an intuitive UI for Admins, Teachers, and Students to interact with the system via the backend REST API.

---

## Overview

This application consumes the FastAPI backend and handles:

- Authentication (JWT-based login)
- Role-based UI rendering
- Student, lesson, and grade management
- Transcript visualization
- Absenteeism tracking display

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React (Vite) |
| Styling | Tailwind CSS |
| HTTP Client | Axios |
| Routing | React Router |
| State Management | React Hooks (useState, useEffect) |
| Storage | localStorage (JWT token) |

---

## Features

- Login system with JWT token storage
- Role-based dashboard rendering (Admin / Teacher / Student)
- Protected routes (unauthorized users redirected)
- Student listing and management
- Lesson creation and editing
- Grade assignment and updates
- Transcript page with pass/fail status
- Absenteeism visualization (30% fail rule reflected in UI)
- API error handling and feedback messages

---

## Project Structure

```text
frontend/
├── src/
│   ├── api/            # Axios instance & API calls
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page-level components
│   ├── routes/         # Route protection logic
│   ├── hooks/          # Custom hooks (auth, etc.)
│   ├── utils/          # Helper functions
│   ├── App.jsx         # Main app component
│   └── main.jsx        # Entry point
├── public/
└── index.html

---

### Frontend README → EKLE

```markdown
## Running the Frontend (Standalone)

```bash
cd frontend
npm install
npm run dev
