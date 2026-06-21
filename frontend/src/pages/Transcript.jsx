import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getMyTranscript, getStudentComment, getStudentRecommendations } from '../services/api';

/**
 * Custom text parser sub-component that compiles LLM raw markdown output strings 
 * into clean React elements seamlessly without importing external packages.
 */
function FormattedAiText({ text }) {
  if (!text) return null;

  const lines = text.split('\n').filter(line => line.trim() !== '');

  return (
    <div className="space-y-2">
      {lines.map((line, idx) => {
        // Parse and split plain strings along bold regex indicator tags systematically
        const parts = line.split(/\*\frac{.*}{.*}/g || /\*\*(.*?)\*\*/g).map((part, i) =>
          i % 2 === 1 ? <strong key={i} className="font-semibold text-gray-900">{part}</strong> : part
        );

        const isBullet = line.trim().startsWith('- ') || line.trim().startsWith('• ');
        const isNumbered = /^\d+\.\s/.test(line.trim());
        const isHeading = line.trim().startsWith('###') || line.trim().startsWith('##');

        if (isHeading) {
          const cleaned = line.replace(/^#{2,3}\s*/, '');
          return (
            <p key={idx} className="text-sm font-bold text-gray-800 mt-3 mb-1 uppercase tracking-wide">
              {cleaned}
            </p>
          );
        }

        if (isBullet) {
          const cleaned = line.replace(/^[-•]\s*/, '');
          const bulletParts = cleaned.split(/\*\*(.*?)\*\*/g).map((part, i) =>
            i % 2 === 1 ? <strong key={i} className="font-semibold text-gray-900">{part}</strong> : part
          );
          return (
            <div key={idx} className="flex items-start gap-2">
              <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-indigo-400 flex-shrink-0" />
              <p className="text-sm text-gray-700 leading-relaxed">{bulletParts}</p>
            </div>
          );
        }

        if (isNumbered) {
          const match = line.match(/^(\d+)\.\s(.*)/);
          if (match) {
            const num = match[1];
            const content = match[2].split(/\*\frac{.*}{.*}/g || /\*\*(.*?)\*\*/g).map((part, i) =>
              i % 2 === 1 ? <strong key={i} className="font-semibold text-gray-900">{part}</strong> : part
            );
            return (
              <div key={idx} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold flex items-center justify-center mt-0.5">
                  {num}
                </span>
                <p className="text-sm text-gray-700 leading-relaxed">{content}</p>
              </div>
            );
          }
        }

        return (
          <p key={idx} className="text-sm text-gray-700 leading-relaxed">{parts}</p>
        );
      })}
    </div>
  );
}

/**
 * Unified presentational card interface designed to frame volatile asynchronous AI responses layout contexts.
 */
function AiCard({ title, icon, content, loading, error, accentClass, bgClass }) {
  return (
    <div className={`rounded-3xl border border-gray-100 shadow-sm overflow-hidden flex flex-col ${bgClass}`}>
      <div className={`px-6 py-4 border-b border-white/40 flex items-center gap-3 ${accentClass}`}>
        <span className="text-sm">{icon}</span>
        <h2 className="text-sm font-bold text-white uppercase tracking-widest">{title}</h2>
      </div>

      <div className="px-6 py-5 flex-1">
        {loading && (
          <div className="space-y-3">
            {/* Skeletal placeholders providing crisp contrast metrics over baseline layouts */}
            <div className="h-3 bg-gray-200/70 animate-pulse rounded-full w-3/4" />
            <div className="h-3 bg-gray-200/70 animate-pulse rounded-full w-full" />
            <div className="h-3 bg-gray-200/70 animate-pulse rounded-full w-5/6" />
            <div className="h-3 bg-gray-200/70 animate-pulse rounded-full w-2/3" />
            <p className="text-xs text-gray-400 mt-4 italic animate-pulse">AI is analyzing your academic records...</p>
          </div>
        )}

        {!loading && error && (
          <div className="flex items-center gap-2 text-red-600 bg-red-50 rounded-xl px-4 py-3">
            <span>⚠️</span>
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {!loading && !error && content && (
          <FormattedAiText text={content} />
        )}
      </div>
    </div>
  );
}

function Transcript() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [transcript, setTranscript] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [comment, setComment] = useState('');
  const [commentLoading, setCommentLoading] = useState(true);
  const [commentError, setCommentError] = useState('');

  const [recommendations, setRecommendations] = useState('');
  const [recommendationsLoading, setRecommendationsLoading] = useState(true);
  const [recommendationsError, setRecommendationsError] = useState('');

  useEffect(() => {
    if (!user?.user_id) {
      setError('User information not found. Please log in again.');
      setLoading(false);
      setCommentLoading(false);
      setRecommendationsLoading(false);
      return;
    }

    const fetchTranscript = async () => {
      try {
        const data = await getMyTranscript(user.user_id);
        setTranscript(data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load transcript.');
      } finally {
        setLoading(false);
      }
    };

    const fetchComment = async () => {
      try {
        const data = await getStudentComment(user.user_id);
        setComment(data.comment);
      } catch (err) {
        setCommentError(err.response?.data?.detail || 'Could not load AI review.');
      } finally {
        setCommentLoading(false);
      }
    };

    const fetchRecommendations = async () => {
      try {
        const data = await getStudentRecommendations(user.user_id);
        setRecommendations(data.recommendations);
      } catch (err) {
        setRecommendationsError(err.response?.data?.detail || 'Could not load AI study guide.');
      } finally {
        setRecommendationsLoading(false);
      }
    };

    // Fire off asynchronous retrieval pipes concurrently toward background nodes
    fetchTranscript();
    fetchComment();
    fetchRecommendations();
  }, [user]);

  // Prune initial tracking structures to compile active score matrices exclusively
  const visibleTranscript = transcript.filter(t => t.grade_type !== 'Enrollment');
  const passed = visibleTranscript.filter(t => t.status === 'Passed').length;
  const failed = visibleTranscript.filter(t => t.status !== 'Passed').length;
  
  // Aggregate numeric means using accumulator reductions safely
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

        {/* Action Header and Descriptive Meta Subtitle */}
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
          <button
            onClick={() => navigate('/')}
            className="py-2 px-5 bg-white border border-gray-200 text-gray-600 rounded-2xl font-semibold hover:bg-gray-50 transition-all shadow-sm"
          >
            ← Back to Dashboard
          </button>
        </div>

        {/* Aggregated Institutional Statistical Widgets Matrix */}
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

        {/* ── AI CARDS DISPLAY SEGMENT ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-8">
          <AiCard
            title="AI Academic Performance Review"
            icon="✨"
            content={comment}
            loading={commentLoading}
            error={commentError}
            accentClass="bg-indigo-600"
            bgClass="bg-indigo-50/40"
          />
          <AiCard
            title="Personalized AI Study Guide"
            icon="✨"
            content={recommendations}
            loading={recommendationsLoading}
            error={recommendationsError}
            accentClass="bg-violet-600"
            bgClass="bg-violet-50/40"
          />
        </div>

        {/* Formal Cumulative Document Grid Table Viewport */}
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
          {loading ? (
            <div className="p-8 space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-14 bg-gray-100 animate-pulse rounded-2xl" />
              ))}
            </div>
          ) : error ? (
            <div className="p-12 text-center">
              <p className="text-red-500 font-medium">{error}</p>
            </div>
          ) : transcript.length === 0 ? (
            <div className="p-12 text-center">
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
                        <span className="text-xs font-bold text-indigo-500 bg-indigo-50 px-2 py-1 rounded-md">
                          {item.lesson_code}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm font-semibold text-gray-800">{item.lesson_name}</td>
                      <td className="px-6 py-4 text-center">
                        <span className="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-1 rounded-md">
                          {item.grade_type || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`text-2xl font-extrabold ${getGradeColor(item.grade_value)}`}>
                          {item.grade_value}
                        </span>
                      </td>
                      {/* Attendance Tracking Parameterized Row Unit */}
                      <td className="px-6 py-4 text-center text-sm text-gray-600 font-medium">
                        {item.absenteeism_count !== undefined ? `${item.absenteeism_count} days` : '-'}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`text-xs font-bold px-3 py-1.5 rounded-full ${getStatusStyle(item.status)}`}>
                          {item.status}
                        </span>
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