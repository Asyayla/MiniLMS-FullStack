import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import { useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Chatbot from "./components/Chatbot";
import CreateLesson from "./pages/CreateLesson";
import StudentManagement from "./pages/StudentManagement";
import Transcript from "./pages/Transcript";
import ManageUsers from "./pages/ManageUsers";
import EditLesson from "./pages/EditLesson";
import ProfileSettings from "./pages/ProfileSettings";

/**
 * Temporary fallback scaffolding component designed to represent feature sets
 * that are currently undergoing active software development.
 */
const PageUnderConstruction = ({ title }) => (
  <div className="p-8 bg-gray-50 min-h-screen flex items-center justify-center">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-800 mb-4">🚧 {title}</h1>
      <p className="text-gray-600">This page will be available soon.</p>
    </div>
  </div>
);

function App() {
  // Extract state variables directly from the core global authentication context frame
  const { token, user } = useAuth();   

  return (
    <Router>
      <div className="App">
        {/* Persistent Layout Components: Rendered globally across all routes. Internal guards handle visual states. */}
        <Navbar /> 
        <Chatbot /> 

        <Routes>
          {/*
           AUTHENTICATION GUARD: 
           If the session token exists, mount the primary Dashboard dashboard frame.
           Otherwise, block lifecycle execution and intercept redirect loops back to /login.
           */}
          <Route
            path="/" 
            element={token ? <Dashboard /> : <Navigate to="/login" />} 
           />

          {/* Login Route: Prevents already authenticated active users from hitting the credentials page redundantly */}
          <Route
            path="/login"
            element={!token ? <Login /> : <Navigate to="/" />} 
            />

          {/* Academic Provisioning Route - Strictly restricted to Teacher or Admin roles via internal assertion */}
          <Route 
            path="/create-lesson" 
            element={
              token && (user?.role === 'teacher' || user?.role === 'admin') 
              ? <CreateLesson /> 
              : <Navigate to="/" />
            } 
          />

          {/* Secured Profile Configurations Route */}
          <Route
            path="/profile"
            element={token ? <ProfileSettings /> : <Navigate to="/login" />}
          />

          {/* Student Document Transcript Viewport Route - Strictly restricted to the Student profile role */}
          <Route
            path="/transcript"
            element={token && user?.role === 'student' ? <Transcript /> : <Navigate to="/" />}
          />

          {/* Administrative Core - Identity Profile Directory Management Route */}
          <Route
            path="/admin/manage-users"
            element={token && user?.role === 'admin' ? <ManageUsers /> : <Navigate to="/" />}
          />

          {/* Administrative Core - Curriculum Modification Entry Route */}
          <Route
            path="/admin/edit-lesson/:id"
            element={token && user?.role === 'admin' ? <EditLesson /> : <Navigate to="/" />}
          />

          {/* Instructor Core - Student Rosters Grade Modification Viewport Route */}
          <Route
            path="/lesson/:id/students"
            element={
              token && (user?.role === 'teacher' || user?.role === 'admin') 
              ? <StudentManagement /> 
              : <Navigate to="/" />}
          />

          {/* Wildcard Fallback Route: Intercepts unmapped 404 paths and resets navigation loops back toward /login safely */}
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;