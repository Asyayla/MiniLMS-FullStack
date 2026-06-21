# MiniLMS — Frontend (React + Vite)

The frontend of MiniLMS is a single-page application built with React 18 and Vite. It provides role-based UI for Admins, Teachers, and Students to interact with the backend REST API, including four integrated AI modules surfaced directly inside existing workflows.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 18+ (via Vite) |
| Styling | Tailwind CSS |
| HTTP Client | Axios |
| Routing | React Router |
| State Management | React Context API + Hooks |
| Auth Storage | localStorage (JWT token) |

---

## Features

### Core LMS

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

### ✨ AI Capability Layer

| Module | Location | Visible To |
|--------|----------|------------|
| ✨ AI Academic Performance Review | `pages/Transcript.jsx` | Student |
| ✨ Personalized AI Study Guide | `pages/Transcript.jsx` | Student |
| ✨ AI Academic Mentor Chatbot | `components/Chatbot.jsx` (global, fixed position) | Student |
| ✨ NLP-Driven Student Filtering | `pages/StudentManagement.jsx` | Teacher / Admin |

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
    │   ├── Navbar.jsx
    │   └── Chatbot.jsx
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
| `App.jsx` | Route definitions, role-based route protection, global mount point for `Chatbot.jsx` |
| `context/AuthContext.jsx` | Global auth state, login/logout, token management |
| `services/api.js` | Centralized Axios instance and all API call functions, including AI endpoints |
| `utils/jwtDecode.js` | JWT token decode utility |
| `components/Navbar.jsx` | Role-aware navigation bar |
| `components/Chatbot.jsx` | ✨ Global persistent AI Academic Mentor Chatbot, student-only |
| `pages/Dashboard.jsx` | Role-based main dashboard with lesson cards |
| `pages/Login.jsx` | Login form |
| `pages/Transcript.jsx` | Student transcript with GPA, pass/fail status, ✨ AI Performance Review and ✨ AI Study Guide cards |
| `pages/StudentManagement.jsx` | Teacher grade management per lesson, ✨ NLP-driven student filtering bar |
| `pages/ManageUsers.jsx` | Admin user management panel |
| `pages/EditLesson.jsx` | Admin lesson edit and delete |
| `pages/ProfileSettings.jsx` | Password change for all roles |

---

## ✨ AI Module Integration

### AI Academic Performance Review & Personalized AI Study Guide

**Surface:** `pages/Transcript.jsx`

On mount, the page issues three independent, parallel requests: the transcript itself, `getStudentComment(studentId)`, and `getStudentRecommendations(studentId)`. Each has its own `loading` and `error` state, so a slow or failed AI response never blocks the transcript table from rendering.

Layout grid:

```text
┌─────────────────────────────┬─────────────────────────────┐
│ ✨ AI Academic Performance   │ ✨ Personalized AI Study     │
│    Review                    │    Guide                      │
│  (indigo accent card)         │  (violet accent card)         │
└─────────────────────────────┴─────────────────────────────┘
┌───────────────────────────────────────────────────────────┐
│                     Transcript Table                          │
└───────────────────────────────────────────────────────────┘
```

Both cards render through a shared `FormattedAiText` component — a lightweight, dependency-free custom parser that splits plain strings along bold tags and maps lists emitted by the LLM into standard React elements without pulling in any external markdown libraries.

### AI Academic Mentor Chatbot

**Surface:** `components/Chatbot.jsx`, mounted globally in `App.jsx`

The chatbot is mounted outside `<Routes>`, directly beside `<Navbar />`, so it persists across every page navigation without unmounting. Visibility is gated entirely client-side on `user?.role === 'student'`; non-student roles never render the trigger button.

```text
App.jsx
 └── <Navbar />
 └── <Chatbot />     ← fixed bottom-6 right-6, persists across all routes
 └── <Routes> ... </Routes>
```

Interaction flow:

1. User sends a message → appended to local `messages` state as `sender: 'user'`.
2. A `typing` placeholder message is appended, rendered as an animated indicator.
3. `sendChatBotMessage(messageText)` calls `POST /students/chat`.
4. The placeholder is removed and replaced with the model's response (`sender: 'bot'`), featuring a clean, optimized interface displaying an inline `AI` branding identifier tag and a localized header wrapper anchored with a dynamic `✨` icon.

The component never accepts or transmits a student ID from the client — the backend resolves identity from the JWT, so the frontend cannot be used to request another student's academic context even by accident.

### NLP-Driven Student Filtering

**Surface:** `pages/StudentManagement.jsx`

A full-width search bar sits directly above the existing student grade table, with a ✨ AI Search trigger and a placeholder demonstrating supported phrasing (for example: `"Find students with GPA desc"` or `"Show students with absenteeism gte 3"`).

```text
┌───────────────────────────────────────────────────────────┐
│ ✨  [ Ask AI to filter students...            ]  AI Search   │
└───────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────┐
│                  Lesson Students Table                        │
└───────────────────────────────────────────────────────────┘
```

On submit, `executeAiQuery(queryText)` calls `POST /students/ai-query`, which returns a `results` array shaped according to which of the backend's closed query actions was matched (`list_students`, `filter_absenteeism`, `filter_grade`, or `unknown`).

The frontend maintains two distinct state arrays:

| State | Purpose |
|-------|---------|
| `students` | The original, untouched roster fetched from `getLessonStudents` |
| `displayedStudents` | The list actually rendered by the table — either the original roster or the AI-filtered result set |

A normalization layer (`normalizeAiResult`) maps each of the backend's polymorphic result shapes into the exact entry contract the existing table and grade-edit modal already expect, so AI-filtered rows remain fully interactive — including grade editing — without any change to the table's rendering logic. A ✕ **Clear Filter** control restores `displayedStudents` from the untouched `students` array at any time.

---

## API Service Layer — AI Functions

`services/api.js` exposes four AI-specific functions alongside the existing LMS calls:

| Function | Endpoint | Returns |
|----------|----------|---------|
| `getStudentComment(studentId)` | `GET /students/{id}/comment` | `{ student_id, comment }` |
| `getStudentRecommendations(studentId)` | `GET /students/{id}/recommendations` | `{ student_id, recommendations }` |
| `executeAiQuery(queryText)` | `POST /students/ai-query` | `{ action, parsed_filter, results }` |
| `sendChatBotMessage(messageText)` | `POST /students/chat` | `{ student_id, message, response }` |

All four route through the same Axios instance as the rest of the application, inheriting the existing Bearer token interceptor and 401 redirect-to-login behavior automatically.

---

## Role-Based Access

| Page / Component | Admin | Teacher | Student |
|-------------------|-------|---------|---------|
| Dashboard | ✓ | ✓ | ✓ |
| Create Lesson | ✓ | ✓ | — |
| Edit Lesson | ✓ | — | — |
| Manage Users | ✓ | — | — |
| Student Management | ✓ | ✓ | — |
| ✨ NLP Student Filtering | ✓ | ✓ | — |
| Transcript | — | — | ✓ |
| ✨ AI Performance Review | — | — | ✓ |
| ✨ AI Study Guide | — | — | ✓ |
| ✨ AI Mentor Chatbot | — | — | ✓ |
| Profile Settings | ✓ | ✓ | ✓ |

---

## Setup and Run

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

> Backend must be running at `http://localhost:8000` before starting the frontend, including a valid `OPENROUTER_API_KEY` for AI module responses.

✓ All four AI surfaces verified against live backend endpoints
✓ Chatbot identity scoping verified — no client-supplied student ID accepted
⚠️ AI cards on `Transcript.jsx` degrade gracefully with an inline error state if the backend AI service is unreachable; the transcript table itself remains fully functional