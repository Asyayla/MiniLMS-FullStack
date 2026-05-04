import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

function Navbar() {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();

  if (!token) return null;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-indigo-950 text-white shadow-lg border-b border-indigo-900">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <Link to="/" className="text-xl font-black tracking-wider text-white hover:text-indigo-200 transition-colors">
              MINI LMS
            </Link>
            <div className="hidden md:flex items-center gap-1">
              <Link to="/" className="hover:bg-indigo-800 px-4 py-2 rounded-lg text-sm font-medium text-indigo-100 hover:text-white transition-all">
                Dashboard
              </Link>
              {user?.role === 'teacher' && (
                <Link to="/create-lesson" className="hover:bg-indigo-800 px-4 py-2 rounded-lg text-sm font-medium text-indigo-100 hover:text-white transition-all">
                  Create Lesson
                </Link>
              )}
              {user?.role === 'admin' && (
                <Link to="/admin/manage-users" className="hover:bg-indigo-800 px-4 py-2 rounded-lg text-sm font-medium text-indigo-100 hover:text-white transition-all">
                  Manage Users
                </Link>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-indigo-900 px-3 py-1.5 rounded-xl">
              <span className="text-sm text-indigo-200 font-medium">{user?.username}</span>
              <span className="text-[10px] font-bold bg-indigo-600 text-white px-2 py-0.5 rounded-md uppercase tracking-wider">
                {user?.role}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 px-4 py-1.5 rounded-lg text-sm font-bold transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;