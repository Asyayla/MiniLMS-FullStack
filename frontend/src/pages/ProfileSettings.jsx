import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { changePassword } from '../services/api';

function ProfileSettings() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.new_password !== form.confirm_password) {
      setError('New passwords do not match.');
      return;
    }
    if (form.new_password.length < 6) {
      setError('New password must be at least 6 characters.');
      return;
    }

    setSubmitting(true);
    try {
      await changePassword(form.current_password, form.new_password);
      setSuccessMsg('Password changed successfully. Please log in again.');
      setForm({ current_password: '', new_password: '', confirm_password: '' });
      setTimeout(() => {
        logout();
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to change password.');
    } finally {
      setSubmitting(false);
    }
  };

  const getRoleBadge = (role) => {
    if (role === 'admin') return 'bg-red-50 text-red-600 border border-red-200';
    if (role === 'teacher') return 'bg-emerald-50 text-emerald-600 border border-emerald-200';
    return 'bg-indigo-50 text-indigo-600 border border-indigo-200';
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen font-sans">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 flex items-center gap-3">
              <span className="w-2 h-9 bg-indigo-600 rounded-full"></span>
              Profile Settings
            </h1>
            <p className="text-gray-500 mt-1 ml-5">Manage your account settings</p>
          </div>
          <button onClick={() => navigate('/')} className="py-2 px-5 bg-white border border-gray-200 text-gray-600 rounded-2xl font-semibold hover:bg-gray-50 transition-all shadow-sm">
            ← Dashboard
          </button>
        </div>

        {/* User Info Card */}
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Account Information</h2>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-indigo-100 rounded-2xl flex items-center justify-center text-2xl font-extrabold text-indigo-600">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">{user?.username}</p>
              <span className={`text-xs font-bold px-3 py-1 rounded-full capitalize ${getRoleBadge(user?.role)}`}>
                {user?.role}
              </span>
            </div>
          </div>
        </div>

        {/* Change Password Card */}
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8">
          <h2 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-6">Change Password</h2>

          {successMsg && (
            <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-2xl text-sm font-medium">
              ✓ {successMsg}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Current Password</label>
              <input
                type="password" name="current_password" value={form.current_password}
                onChange={handleChange} required placeholder="Enter current password"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">New Password</label>
              <input
                type="password" name="new_password" value={form.new_password}
                onChange={handleChange} required placeholder="Minimum 6 characters"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Confirm New Password</label>
              <input
                type="password" name="confirm_password" value={form.confirm_password}
                onChange={handleChange} required placeholder="Repeat new password"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-xs text-red-600 font-medium">{error}</div>
            )}

            <button
              type="submit" disabled={submitting}
              className="w-full py-3 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all disabled:opacity-50"
            >
              {submitting ? 'Saving...' : 'Change Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ProfileSettings;