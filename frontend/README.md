# MiniLMS — Frontend (React + Vite)

The frontend of MiniLMS is a single-page application built with React and Vite. It provides role-based UI for Admins, Teachers, and Students to interact with the backend REST API.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React (via Vite) |
| Styling | Tailwind CSS |
| HTTP Client | Axios |
| Routing | React Router |
| State Management | React Context API + Hooks |
| Auth Storage | localStorage (JWT token) |

---

## Features

- JWT-based login with token storage
- Role-based dashboard (Admin / Teacher / Student)
- Protected routes with automatic redirect
- Course enrollment and unenrollment
- Grade viewing per course (modal) and full transcript page
- Absenteeism status display (30% fail rule)
- Admin: user management (create, edit role, delete)
- Admin: lesson management (create, edit, delete)
- Teacher: student and grade management per lesson
- Profile settings with password change

---

## Project Structure

```text
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── components/
    │   └── Navbar.jsx
    ├── context/
    │   └── AuthContext.jsx
    ├── pages/
    │   ├── Login.jsx
    │   ├── Dashboard.jsx
    │   ├── CreateLesson.jsx
    │   ├── EditLesson.jsx
    │   ├── StudentManagement.jsx
    │   ├── ManageUsers.jsx
    │   ├── Transcript.jsx
    │   └── ProfileSettings.jsx
    ├── services/
    │   └── api.js
    └── utils/
        └── jwtDecode.js
```

### Key Files

| File | Description |
|------|-------------|
| `App.jsx` | Route definitions and role-based route protection |
| `context/AuthContext.jsx` | Global auth state, login/logout, token management |
| `services/api.js` | Centralized Axios instance and all API call functions |
| `utils/jwtDecode.js` | JWT token decode utility |
| `components/Navbar.jsx` | Role-aware navigation bar |
| `pages/Dashboard.jsx` | Role-based main dashboard with lesson cards |
| `pages/Login.jsx` | Login form |
| `pages/Transcript.jsx` | Student transcript with GPA, pass/fail status |
| `pages/StudentManagement.jsx` | Teacher grade management per lesson |
| `pages/ManageUsers.jsx` | Admin user management panel |
| `pages/EditLesson.jsx` | Admin lesson edit and delete |
| `pages/ProfileSettings.jsx` | Password change for all roles |

---

## Role-Based Access

| Page | Admin | Teacher | Student |
|------|-------|---------|---------|
| Dashboard | ✓ | ✓ | ✓ |
| Create Lesson | ✓ | ✓ | — |
| Edit Lesson | ✓ | — | — |
| Manage Users | ✓ | — | — |
| Student Management | ✓ | ✓ | — |
| Transcript | — | — | ✓ |
| Profile Settings | ✓ | ✓ | ✓ |

---

## Setup and Run

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

> Backend must be running at `http://localhost:8000` before starting the frontend.
