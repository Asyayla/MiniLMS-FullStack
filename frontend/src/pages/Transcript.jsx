import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getMyTranscript } from '../services/api';

function Transcript() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [transcript, setTranscript] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTranscript = async () => {
      if (!user?.user_id) {
        setError('User information not found. Please log in again.');
        setLoading(false);
        return;
      }
      try {
        const data = await getMyTranscript(user.user_id);
        setTranscript(data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load transcript.');
      } finally {
        setLoading(false);
      }
    };
    fetchTranscript();
  }, [user]);

  const visibleTranscript = transcript.filter(t => t.grade_type !== 'Enrollment');
  const passed = visibleTranscript.filter(t => t.status === 'Passed').length;
  const failed = visibleTranscript.filter(t => t.status !== 'Passed').length;
  const average = visibleTranscript.length > 0
    ? (visibleTranscript.reduce((sum, t) => sum + t.grade_value, 0) / visibleTranscript.length).toFixed(1)
    : '-';

  const getStatusStyle = (status) => {
    if (status === 'Passed') return 'bg-emerald-50 text-emerald-700 border border-emerald-200';
    if (status === 'Failed (Absenteeism)') return 'bg-orange-50 text-orange-700 border border-orange-200';
    return 'bg-red-50 text-red-700 border border-red-200';
  };

  const getGradeColor = (value) => {
    if (value >= 50) return 'text-emerald-600';
    return 'text-red-500';
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen font-sans">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 flex items-center gap-3">
              <span className="w-2 h-9 bg-indigo-600 rounded-full"></span>
              My Transcript
            </h1>
            <p className="text-gray-500 mt-1 ml-5">
              Academic record for <span className="font-semibold text-gray-700">{user?.username}</span>
            </p>
          </div>
          <button onClick={() => navigate('/')} className="py-2 px-5 bg-white border border-gray-200 text-gray-600 rounded-2xl font-semibold hover:bg-gray-50 transition-all shadow-sm">
            ← Back to Dashboard
          </button>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 text-center">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">GPA Average</p>
            <p className="text-4xl font-extrabold text-indigo-600">{average}</p>
          </div>
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 text-center">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Passed</p>
            <p className="text-4xl font-extrabold text-emerald-500">{passed}</p>
          </div>
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 text-center">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Failed</p>
            <p className="text-4xl font-extrabold text-red-400">{failed}</p>
          </div>
        </div>

        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
          {loading ? (
            <div className="p-8 space-y-4">
              {[1, 2, 3].map(i => <div key={i} className="h-14 bg-gray-100 animate-pulse rounded-2xl"></div>)}
            </div>
          ) : error ? (
            <div className="p-12 text-center">
              <p className="text-red-500 font-medium">{error}</p>
            </div>
          ) : transcript.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-5xl mb-4">📋</p>
              <p className="text-gray-500 font-medium">No grades recorded yet.</p>
              <p className="text-gray-400 text-sm mt-1">Enroll in courses to see your transcript here.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-100">
                <thead className="bg-indigo-50">
                  <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-indigo-500 uppercase tracking-widest">Course Code</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-indigo-500 uppercase tracking-widest">Course Name</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-indigo-500 uppercase tracking-widest">Type</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-indigo-500 uppercase tracking-widest">Grade</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-indigo-500 uppercase tracking-widest">Attendance</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-indigo-500 uppercase tracking-widest">Status</th>
                  </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                  {visibleTranscript.map((item, idx) => (
                  <tr key={idx} className="hover:bg-indigo-50/30 transition-colors">
                       <td className="px-6 py-4">
                       <span className="text-xs font-bold text-indigo-500 bg-indigo-50 px-2 py-1 rounded-md">{item.lesson_code}</span>
                       </td>
                       <td className="px-6 py-4 text-sm font-semibold text-gray-800">{item.lesson_name}</td>
                       <td className="px-6 py-4 text-center">
                       <span className="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-1 rounded-md">
                            {item.grade_type || 'N/A'}
                       </span>
                       </td>
                       <td className="px-6 py-4 text-center">
                       <span className={`text-2xl font-extrabold ${getGradeColor(item.grade_value)}`}>{item.grade_value}</span>
                       </td>
                       <td className="px-6 py-4 text-center text-sm text-gray-600">{item.absenteeism ?? '-'}%</td>
                       <td className="px-6 py-4 text-center">
                      <span className={`text-xs font-bold px-3 py-1.5 rounded-full ${getStatusStyle(item.status)}`}>{item.status}</span>
                       </td>
                  </tr>
                  ))}
                  </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Transcript;