import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllUsers, registerUser, deleteUser, updateUser } from '../services/api';

function ManageUsers() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [form, setForm] = useState({ username: '', password: '', role: 'student' });
  const [editForm, setEditForm] = useState({ role: 'student' });

  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await getAllUsers();
      setUsers(data);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const handleEditFormChange = (e) => setEditForm({ ...editForm, [e.target.name]: e.target.value });

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await registerUser(form.username, form.password, form.role);
      setSuccessMsg(`User "${form.username}" created successfully.`);
      setForm({ username: '', password: '', role: 'student' });
      setModalOpen(false);
      fetchUsers();
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create user.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditUser = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await updateUser(selectedUser.id, editForm.role);
      setSuccessMsg(`User "${selectedUser.username}" updated successfully.`);
      setEditModalOpen(false);
      setSelectedUser(null);
      fetchUsers();
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update user.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteUser = async (userId, username) => {
    if (!window.confirm(`Are you sure you want to delete "${username}"? This action cannot be undone.`)) return;
    try {
      await deleteUser(userId);
      setSuccessMsg(`User "${username}" deleted successfully.`);
      fetchUsers();
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setSuccessMsg('');
      alert(err.response?.data?.detail || 'Failed to delete user.');
    }
  };

  const openEditModal = (u) => {
    setSelectedUser(u);
    setEditForm({ role: u.role });
    setError('');
    setEditModalOpen(true);
  };

  const getRoleBadge = (role) => {
    if (role === 'admin') return 'bg-red-50 text-red-600 border border-red-200';
    if (role === 'teacher') return 'bg-emerald-50 text-emerald-600 border border-emerald-200';
    return 'bg-indigo-50 text-indigo-600 border border-indigo-200';
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen font-sans">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 flex items-center gap-3">
              <span className="w-2 h-9 bg-indigo-600 rounded-full"></span>
              Manage Users
            </h1>
            <p className="text-gray-500 mt-1 ml-5">Admin panel — view, create, edit and delete system users</p>
          </div>
          <div className="flex gap-3">
            <button onClick={() => navigate('/')} className="py-2 px-5 bg-white border border-gray-200 text-gray-600 rounded-2xl font-semibold hover:bg-gray-50 transition-all shadow-sm">
              ← Dashboard
            </button>
            <button onClick={() => { setModalOpen(true); setError(''); }} className="py-2 px-5 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100">
              + New User
            </button>
          </div>
        </div>

        {successMsg && (
          <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-2xl text-sm font-medium">
            ✓ {successMsg}
          </div>
        )}

        {/* Stats - 4 kart */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-3xl p-5 shadow-sm border border-gray-100 text-center">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Total</p>
            <p className="text-3xl font-extrabold text-gray-800">{users.length}</p>
          </div>
          <div className="bg-white rounded-3xl p-5 shadow-sm border border-gray-100 text-center">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Admins</p>
            <p className="text-3xl font-extrabold text-red-500">{users.filter(u => u.role === 'admin').length}</p>
          </div>
          <div className="bg-white rounded-3xl p-5 shadow-sm border border-gray-100 text-center">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Teachers</p>
            <p className="text-3xl font-extrabold text-emerald-500">{users.filter(u => u.role === 'teacher').length}</p>
          </div>
          <div className="bg-white rounded-3xl p-5 shadow-sm border border-gray-100 text-center">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Students</p>
            <p className="text-3xl font-extrabold text-indigo-500">{users.filter(u => u.role === 'student').length}</p>
          </div>
        </div>

        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
          {loading ? (
            <div className="p-8 space-y-4">
              {[1,2,3].map(i => <div key={i} className="h-12 bg-gray-100 animate-pulse rounded-2xl"></div>)}
            </div>
          ) : users.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-5xl mb-4">👥</p>
              <p className="text-gray-500 font-medium">No users found in the system.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-100">
                <thead className="bg-indigo-50">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-widest">#</th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-widest">Username</th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-widest">Role</th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-indigo-600 uppercase tracking-widest">User ID</th>
                    <th className="px-6 py-4 text-right text-xs font-bold text-indigo-600 uppercase tracking-widest">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {users.map((u, idx) => (
                    <tr key={idx} className="hover:bg-indigo-50/30 transition-colors">
                      <td className="px-6 py-4 text-sm text-gray-500">{idx + 1}</td>
                      <td className="px-6 py-4 text-sm font-semibold text-gray-900">{u.username}</td>
                      <td className="px-6 py-4">
                        <span className={`text-xs font-bold px-3 py-1.5 rounded-full capitalize ${getRoleBadge(u.role)}`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-400 font-mono">#{u.id}</td>
                      <td className="px-6 py-4 text-right flex justify-end gap-2">
                        <button
                          onClick={() => openEditModal(u)}
                          className="py-1.5 px-3 bg-indigo-50 text-indigo-600 border border-indigo-200 rounded-xl text-xs font-bold hover:bg-indigo-100 transition-all"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteUser(u.id, u.username)}
                          className="py-1.5 px-3 bg-red-50 text-red-600 border border-red-200 rounded-xl text-xs font-bold hover:bg-red-100 transition-all"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Create User Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-3xl p-8 shadow-2xl border border-gray-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-1">Create New User</h3>
            <p className="text-sm text-gray-500 mb-6">Add a new student, teacher, or admin to the system.</p>
            <form onSubmit={handleCreateUser} className="space-y-5">
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Username</label>
                <input type="text" name="username" value={form.username} onChange={handleFormChange} required placeholder="e.g. john_doe"
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-400 outline-none transition-all" />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Password</label>
                <input type="password" name="password" value={form.password} onChange={handleFormChange} required placeholder="Minimum 6 characters"
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-400 outline-none transition-all" />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Role</label>
                <select name="role" value={form.role} onChange={handleFormChange}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-400 outline-none transition-all">
                  <option value="student">Student</option>
                  <option value="teacher">Teacher</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              {error && <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-xs text-red-600 font-medium">{error}</div>}
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setModalOpen(false)}
                  className="flex-1 py-3 bg-white border border-gray-200 text-gray-600 rounded-2xl font-bold hover:bg-gray-50 transition-all">
                  Cancel
                </button>
                <button type="submit" disabled={submitting}
                  className="flex-1 py-3 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all disabled:opacity-50">
                  {submitting ? 'Creating...' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {editModalOpen && selectedUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-3xl p-8 shadow-2xl border border-gray-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-1">Edit User</h3>
            <p className="text-sm text-gray-500 mb-6">Change role for <span className="font-semibold text-gray-700">{selectedUser.username}</span></p>
            <form onSubmit={handleEditUser} className="space-y-5">
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Role</label>
                <select name="role" value={editForm.role} onChange={handleEditFormChange}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-400 outline-none transition-all">
                  <option value="student">Student</option>
                  <option value="teacher">Teacher</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              {error && <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-xs text-red-600 font-medium">{error}</div>}
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setEditModalOpen(false)}
                  className="flex-1 py-3 bg-white border border-gray-200 text-gray-600 rounded-2xl font-bold hover:bg-gray-50 transition-all">
                  Cancel
                </button>
                <button type="submit" disabled={submitting}
                  className="flex-1 py-3 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all disabled:opacity-50">
                  {submitting ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default ManageUsers;