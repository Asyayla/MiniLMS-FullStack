# 🎓 MiniLMS — Frontend (React + Vite)

The frontend of MiniLMS is a modern single-page application built with React and Vite. It provides an intuitive, role-based UI for Admins, Teachers, and Students to interact with the system via the FastAPI backend.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Library** | React (Vite) |
| **Styling** | Tailwind CSS |
| **HTTP Client** | Axios |
| **Routing** | React Router v6 |
| **State Management** | React Context API (AuthContext) |
| **Storage** | localStorage (JWT token storage) |

---

## 📂 Project Structure
```text
frontend/
├── src/
│   ├── assets/         # Static assets (images, hero sections, logos)
│   ├── components/     # Reusable UI components (Navbar, ProtectedRoute)
│   ├── context/        # Global state management (AuthContext for session handling)
│   ├── pages/          # Page components (Dashboard, Transcript, ManageUsers, etc.)
│   ├── services/       # Centralized API service configuration (api.js)
│   ├── utils/          # Helper functions and JWT decoding utilities
│   ├── App.jsx         # Main application component and route definitions
│   └── main.jsx        # Application entry point
├── public/             # Static public files
├── .env                # Environment variables (API Base URL configuration)
└── tailwind.config.js  # Tailwind CSS styling configuration
