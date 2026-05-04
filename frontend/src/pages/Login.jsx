import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../services/api';
import { useAuth } from '../context/AuthContext.jsx';
import { decodeToken } from '../utils/jwtDecode';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const data = await loginUser(username, password);
      if (!data.access_token) throw new Error("Token not found");
      let userData = {
        username: data.username || username,
        role: data.role,
        user_id: data.user_id
      };
      try {
        const decoded = decodeToken(data.access_token);
        userData.user_id = userData.user_id || decoded?.user_id;
        userData.role = userData.role || decoded?.role;
      } catch (decodeErr) {
        console.warn("Token decode failed, using backend data.");
      }
      login(userData, data.access_token);
      navigate('/');
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed. Please check credentials.';
      setError(message);
    }
  };

  return (
    <div className="min-h-screen bg-indigo-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo / Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-black text-white tracking-wider mb-2">MINI LMS</h1>
          <p className="text-indigo-300 text-sm">Learning Management System</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Welcome back</h2>
          <p className="text-gray-500 text-sm mb-8">Sign in to your account to continue</p>

          {error && (
            <div className="p-3 mb-6 text-sm text-red-700 bg-red-50 border border-red-200 rounded-2xl font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
                Username
              </label>
              <input
                type="text"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all text-gray-900"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Enter your username"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
                Password
              </label>
              <input
                type="password"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all text-gray-900"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter your password"
              />
            </div>
            <button
              type="submit"
              className="w-full py-3 px-4 rounded-2xl text-white bg-indigo-600 hover:bg-indigo-700 font-bold transition-all shadow-lg shadow-indigo-200 active:scale-95"
            >
              Sign In
            </button>
          </form>
        </div>

        <p className="text-center text-indigo-400 text-xs mt-6">
          Mini LMS — Academic Management Platform
        </p>
      </div>
    </div>
  );
}

export default Login;