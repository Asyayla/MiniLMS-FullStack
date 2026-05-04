import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getLessonById, updateLesson, deleteLesson, getAllUsers } from '../services/api';

function EditLesson() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [form, setForm] = useState({ name: '', code: '', teacher_id: '' });
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [lesson, users] = await Promise.all([getLessonById(id), getAllUsers()]);
        setForm({ name: lesson.name, code: lesson.code, teacher_id: lesson.teacher_id });
        setTeachers(users.filter(u => u.role === 'teacher' || u.role === 'admin'));
      } catch (err) {
        setError('Failed to load lesson data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleUpdate = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await updateLesson(id, { ...form, teacher_id: Number(form.teacher_id) });
      setSuccessMsg('Lesson updated successfully.');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update lesson.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this lesson? All grades will also be deleted.')) return;
    try {
      await deleteLesson(id);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete lesson.');
    }
  };

  if (loading) return (
    <div className="p-8 bg-gray-50 min-h-screen flex items-center justify-center">
      <div className="text-gray-400 font-medium">Loading lesson...</div>
    </div>
  );

  return (
    <div className="p-8 bg-gray-50 min-h-screen font-sans">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 flex items-center gap-3">
              <span className="w-2 h-9 bg-indigo-500 rounded-full"></span>
              Edit Lesson
            </h1>
            <p className="text-gray-500 mt-1 ml-5">Update lesson details or delete it from the system.</p>
          </div>
          <button onClick={() => navigate('/')} className="py-2 px-5 bg-white border border-gray-200 text-gray-600 rounded-2xl font-semibold hover:bg-gray-50 transition-all shadow-sm">
            ← Dashboard
          </button>
        </div>

        {successMsg && (
          <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-2xl text-sm font-medium">
            ✓ {successMsg}
          </div>
        )}

        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8">
          <form onSubmit={handleUpdate} className="space-y-6">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Lesson Name</label>
              <input
                type="text" name="name" value={form.name} onChange={handleChange} required
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-amber-400 outline-none transition-all"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Lesson Code</label>
              <input
                type="text" name="code" value={form.code} onChange={handleChange} required
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-amber-400 outline-none transition-all"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Assigned Teacher</label>
              <select
                name="teacher_id" value={form.teacher_id} onChange={handleChange} required
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-amber-400 outline-none transition-all"
              >
                <option value="">Select a teacher...</option>
                {teachers.map(t => (
                  <option key={t.id} value={t.id}>{t.username} ({t.role})</option>
                ))}
              </select>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-xs text-red-600 font-medium">{error}</div>
            )}

            <div className="flex gap-3 pt-2">
              <button
                type="button" onClick={handleDelete}
                className="py-3 px-6 bg-red-50 text-red-600 border border-red-200 rounded-2xl font-bold hover:bg-red-100 transition-all"
              >
                Delete Lesson
              </button>
              <button
                type="submit" disabled={submitting}
                className="flex-1 py-3 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all disabled:opacity-50"
              >
                {submitting ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default EditLesson;