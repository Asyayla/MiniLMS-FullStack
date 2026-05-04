import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getLessons, enrollInLesson, getMyTranscript, unenrollFromLesson } from '../services/api';

function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [lessons, setLessons] = useState([]);
  const [enrolledLessonIds, setEnrolledLessonIds] = useState([]);
  const [transcript, setTranscript] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [gradeModal, setGradeModal] = useState(null);

  const rawRole = user?.role || "User";
  const userRole = rawRole.toLowerCase();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getLessons();
        setLessons(data);
        if (userRole === 'student' && user?.user_id) {
          try {
            const transcriptData = await getMyTranscript(user.user_id);
            const ids = transcriptData.map(t => t.lesson_id);
            setEnrolledLessonIds(ids);
            setTranscript(transcriptData);
          } catch {
            // transcript bossa sorun degil
          }
        }
      } catch (err) {
        console.error("Failed to load lessons:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  const handleEnroll = async (lessonId) => {
    setActionLoading(lessonId);
    try {
      await enrollInLesson(lessonId);
      setEnrolledLessonIds(prev => [...prev, lessonId]);
      alert("Enrollment successful! You have been added to the course.");
    } catch (err) {
      alert(err.response?.data?.detail || "Enrollment failed. Please contact administration.");
    } finally {
      setActionLoading(null);
    }
  };

  const handleViewGrades = (lesson) => {
    const lessonGrades = transcript.filter(t => t.lesson_id === lesson.id);
    setGradeModal({ lessonName: lesson.name, lessonCode: lesson.code, grades: lessonGrades });
  };

  const handleUnenroll = async (lessonId) => {
    if (!window.confirm('Are you sure you want to unenroll from this course? Your grades will be deleted.')) return;
    setActionLoading(lessonId);
    try {
      await unenrollFromLesson(lessonId);
      setEnrolledLessonIds(prev => prev.filter(id => id !== lessonId));
      setTranscript(prev => prev.filter(t => t.lesson_id !== lessonId));
      if (gradeModal?.lessonCode === lessons.find(l => l.id === lessonId)?.code) {
        setGradeModal(null);
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to unenroll. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };


  const enrolledLessons = lessons.filter(l => enrolledLessonIds.includes(l.id));
  const availableLessons = lessons.filter(l => !enrolledLessonIds.includes(l.id));

  const LessonCard = ({ lesson, enrolled }) => (
    <div className={`group p-5 bg-white rounded-3xl border transition-all duration-300 ${enrolled ? 'border-emerald-200 hover:shadow-lg' : 'border-gray-100 hover:border-indigo-200 hover:shadow-xl'}`}>
      <div className="flex flex-col h-full">
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-500 bg-indigo-50 px-2 py-1 rounded-md inline-block">
              {lesson.code || "LMS-101"}
            </span>
            {enrolled && (
              <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-600 bg-emerald-50 px-2 py-1 rounded-md">
                Enrolled ✓
              </span>
            )}
          </div>
          <h3 className="font-bold text-gray-900 text-lg group-hover:text-indigo-600 transition-colors">
            {lesson.name}
          </h3>
        </div>
        <div className="mt-auto pt-4 border-t border-gray-50">
          {userRole === 'student' && (
            enrolled ? (
              <div className="space-y-2">
                <button
                  onClick={() => handleViewGrades(lesson)}
                  className="w-full py-2.5 px-4 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-2xl font-bold hover:bg-emerald-100 active:scale-95 transition-all"
                >
                  View Grades
                </button>
                <button
                  disabled={actionLoading === lesson.id}
                  onClick={() => handleUnenroll(lesson.id)}
                  className="w-full py-2 px-4 bg-red-50 text-red-500 border border-red-100 rounded-2xl text-sm font-semibold hover:bg-red-100 active:scale-95 transition-all disabled:opacity-50"
                >
                  {actionLoading === lesson.id ? 'Processing...' : 'Unenroll'}
                </button>
              </div>
            ) : (
              <button
                disabled={actionLoading === lesson.id}
                onClick={() => handleEnroll(lesson.id)}
                className="w-full py-3 px-4 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 active:scale-95 transition-all disabled:opacity-50"
              >
                {actionLoading === lesson.id ? "Processing..." : "Enroll Now"}
              </button>
            )
          )}
          {userRole === 'teacher' && (
            <button
              onClick={() => navigate(`/lesson/${lesson.id}/students`)}
              className="w-full py-3 px-4 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 active:scale-95 transition-all"
              
            >
              Manage Students
            </button>
          )}
          {userRole === 'admin' && (
            <button
              onClick={() => navigate(`/admin/edit-lesson/${lesson.id}`)}
              className="w-full py-3 px-4 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 active:scale-95 transition-all"
            >
              Edit Lesson
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-8 bg-gray-50 min-h-screen font-sans">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            {loading ? (
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 space-y-4">
                {[1, 2, 3].map(i => <div key={i} className="h-24 bg-gray-100 animate-pulse rounded-2xl"></div>)}
              </div>
            ) : userRole === 'student' ? (
              <>
                {enrolledLessons.length > 0 && (
                  <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
                    <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                      <span className="w-2 h-7 bg-emerald-500 rounded-full"></span>
                      My Enrolled Courses
                      <span className="text-sm font-normal text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">{enrolledLessons.length}</span>
                    </h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {enrolledLessons.map(lesson => <LessonCard key={lesson.id} lesson={lesson} enrolled={true} />)}
                    </div>
                  </div>
                )}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
                  <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                    <span className="w-2 h-7 bg-indigo-600 rounded-full"></span>
                    Available Courses
                    <span className="text-sm font-normal text-indigo-600 bg-indigo-50 px-2 py-1 rounded-full">{availableLessons.length}</span>
                  </h2>
                  {availableLessons.length === 0 ? (
                    <p className="text-gray-400 text-center py-8">You are enrolled in all available courses!</p>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {availableLessons.map(lesson => <LessonCard key={lesson.id} lesson={lesson} enrolled={false} />)}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                  <span className="w-2 h-8 bg-indigo-600 rounded-full"></span>
                  {userRole === 'teacher' ? `${user?.username || 'Teacher'}'s Managed Lessons` : 'All Lessons'}
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  {lessons.map(lesson => <LessonCard key={lesson.id} lesson={lesson} enrolled={false} />)}
                </div>
              </div>
            )}
          </div>

          <aside className="space-y-6">
            <div className="bg-gradient-to-br from-slate-900 to-indigo-900 p-8 rounded-3xl text-white shadow-2xl">
              <h3 className="text-xl font-bold mb-1">Welcome Back!</h3>
              <p className="text-indigo-300 text-sm mb-6 italic capitalize">
                Logged in as: <span className="text-white font-bold">{rawRole}</span>
              </p>
              <div className="space-y-3">
                {userRole === 'student' && (
                  <button onClick={() => navigate('/transcript')} className="w-full bg-white/10 hover:bg-white/20 py-3 rounded-2xl text-sm font-semibold transition-all">
                    View My Transcript
                  </button>
                )}
                {userRole === 'admin' && (
                  <button onClick={() => navigate('/admin/manage-users')} className="w-full bg-white/10 hover:bg-white/20 py-3 rounded-2xl text-sm font-semibold transition-all">
                    Manage Users
                  </button>
                )}
                <button onClick={() => navigate('/profile')} className="w-full bg-white/5 hover:bg-white/10 py-3 rounded-2xl text-sm font-semibold transition-all">
                  Profile Settings
                </button>
              </div>
            </div>

            <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">LMS Overview</h4>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 text-sm font-medium">Total Lessons</span>
                <span className="bg-indigo-50 text-indigo-600 px-3 py-1 rounded-full text-sm font-bold">{lessons.length}</span>
              </div>
              {userRole === 'student' && (
                <div className="flex items-center justify-between mt-3">
                  <span className="text-gray-600 text-sm font-medium">Enrolled</span>
                  <span className="bg-emerald-50 text-emerald-600 px-3 py-1 rounded-full text-sm font-bold">{enrolledLessons.length}</span>
                </div>
              )}
            </div>
          </aside>
        </div>
      </div>

      {gradeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white rounded-3xl p-8 shadow-2xl border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{gradeModal.lessonName}</h3>
                <span className="text-xs font-bold text-indigo-500 bg-indigo-50 px-2 py-1 rounded-md">{gradeModal.lessonCode}</span>
              </div>
              <button onClick={() => setGradeModal(null)} className="text-gray-400 hover:text-gray-600 text-2xl font-bold">✕</button>
            </div>
            {gradeModal.grades.filter(g => g.grade_type !== 'Enrollment').length === 0 ? (
              <p className="text-center text-gray-400 py-8">No grades recorded yet for this course.</p>
            ) : (
              <div className="space-y-3">
                {gradeModal.grades.filter(g => g.grade_type !== 'Enrollment').map((g, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-2xl">
                    <span className="text-sm font-medium text-gray-600">{g.grade_type}</span>
                    <div className="flex items-center gap-3">
                      <span className={`text-2xl font-extrabold ${g.grade_value >= 50 ? 'text-emerald-600' : 'text-red-500'}`}>
                        {g.grade_value}
                      </span>
                      <span className={`text-xs font-bold px-2 py-1 rounded-full ${g.status === 'Passed' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
                        {g.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <button
              onClick={() => navigate('/transcript')}
              className="w-full mt-6 py-3 bg-indigo-50 text-indigo-600 rounded-2xl font-bold hover:bg-indigo-100 transition-all"
            >
              View Full Transcript
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;