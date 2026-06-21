import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getLessonStudents, submitGrade, updateGrade, executeAiQuery } from '../services/api';
import { useAuth } from '../context/AuthContext';

function StudentManagement() {
  const { id: lessonId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [students, setStudents] = useState([]);       // Master copy: complete roster returned from the backend
  const [displayedStudents, setDisplayedStudents] = useState([]); // Reactive copy: actively rendered list (filtered or unfiltered)
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [gradeType, setGradeType] = useState('Midterm');
  const [gradeValue, setGradeValue] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // --- AI NLP Query Search State Boundaries ---
  const [aiQuery, setAiQuery] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');
  const [isFiltered, setIsFiltered] = useState(false);
  const [aiResultMeta, setAiResultMeta] = useState(null); // Structural footprint tracking: { action, count }

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const data = await getLessonStudents(lessonId);
        const list = data?.students || data || [];
        setStudents(list);
        setDisplayedStudents(list);
      } catch (err) {
        console.error('Failed to fetch lesson students:', err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [lessonId]);

  const extractStudentInfo = (entry) => {
    const studentObj = entry?.student || entry?.student_data || null;
    const studentId = entry?.student_id || studentObj?.id || entry?.id || null;
    const name = studentObj ? `${studentObj.name || ''} ${studentObj.surname || ''}`.trim() : entry?.name || `Student #${studentId}`;
    const email = studentObj?.email || entry?.email || '';
    return { studentId, name, email };
  };

  /**
   * Data Normalization Broker. 
   * Maps polymorphic JSON structures returned by the LLM NLP filter actions 
   * directly into the unified table component rendering scheme schema layout contracts.
   */
  const normalizeAiResult = (item, action) => {
    const baseStudent = {
      id: item.student_id,
      name: item.name,
      surname: item.surname || '',
      email: item.email || '',
    };

    if (action === 'list_students') {
      return {
        student_id: item.student_id,
        student: baseStudent,
        lastGrade: { type: 'GPA', value: item.gpa },
      };
    }

    if (action === 'filter_absenteeism') {
      return {
        student_id: item.student_id,
        student: baseStudent,
        lastGrade: { type: item.lesson_name, value: `${item.absenteeism} absences` },
      };
    }

    if (action === 'filter_grade') {
      return {
        student_id: item.student_id,
        student: baseStudent,
        lastGrade: { type: item.lesson_name, value: item.grade_value },
      };
    }

    // Unresolved action type boundary fallback
    return {
      student_id: item.student_id,
      student: baseStudent,
      lastGrade: null,
    };
  };

  const handleAiSearch = async () => {
    const trimmed = aiQuery.trim();
    if (!trimmed || aiLoading) return;

    setAiLoading(true);
    setAiError('');

    try {
      // Execute asymmetric NLP query pipeline calculation toward the AI routing gateway
      const data = await executeAiQuery(trimmed);

      if (data.action === 'unknown' || !data.results || data.results.length === 0) {
        setDisplayedStudents([]);
        setAiResultMeta({ action: data.action, count: 0 });
        setIsFiltered(true);
        if (data.action === 'unknown') {
          setAiError(data.message || 'Could not understand the query. Try rephrasing it.');
        }
        return;
      }

      // Compile and bind standardized schemas models array mappings cleanly
      const normalized = data.results.map((item) => normalizeAiResult(item, data.action));
      setDisplayedStudents(normalized);
      setAiResultMeta({ action: data.action, count: normalized.length });
      setIsFiltered(true);
    } catch (err) {
      console.error('AI query failed:', err);
      setAiError(err.response?.data?.detail || 'AI search failed. Please try again.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleAiKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAiSearch();
    }
  };

  const clearAiFilter = () => {
    setAiQuery('');
    setAiError('');
    setAiResultMeta(null);
    setIsFiltered(false);
    setDisplayedStudents(students);
  };

  const openModal = (entry) => {
    setSelectedStudent(entry);
    setGradeType('Midterm');
    setGradeValue('');
    setError('');
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedStudent(null);
    setGradeValue('');
    setGradeType('Midterm');
    setError('');
  };

  const handleSubmitGrade = async (e) => {
    e.preventDefault();
    setError('');

    const value = Number(gradeValue);
    if (Number.isNaN(value) || value < 0 || value > 100) {
      setError('Grade must be a numeric value between 0 and 100.');
      return;
    }

    const studentId = selectedStudent?.student_id || selectedStudent?.student?.id || selectedStudent?.id;
    if (!studentId) {
      setError('Student identification failed.');
      return;
    }

    setSubmitting(true);

    try {
      await submitGrade({
        student_id: studentId,
        lesson_id: Number(lessonId),
        grade_value: value,
        grade_type: gradeType,
        absenteeism_count: 0
      });

      // Synchronize dataset updates across both state catalogs to sustain tracking during live AI filters
      const updateList = (prev) => prev.map((it) => {
        const sid = it?.student_id || it?.student?.id || it?.id;
        if (String(sid) === String(studentId)) {
          return { ...it, lastGrade: { type: gradeType, value } };
        }
        return it;
      });
      setStudents(updateList);
      setDisplayedStudents(updateList);

      closeModal();
    } catch (err) {
      console.error('Grade submission error:', err);
      const serverMessage = err.response?.data?.detail;
      
      // Dynamic Idempotency Catch: If an item already exists, catch exception and switch seamlessly to a PUT update fallback flow
      if (serverMessage === "A grading system already exists for this type.") {
          try {
            const existing = students
               .filter(s => (s.student_id || s.student?.id) === studentId)
               .find(s => s.grade_type === gradeType);
            if (existing?.id) {
               await updateGrade(existing.id, { grade_value: value});
               const updateExisting = (prev) => prev.map(it => {
                     const sid = it?.student_id || it?.student?.id || it?.id;
                     if (String(sid) === String(studentId) && it.grade_type === gradeType) {
                        return { ...it, grade_value: value, lastGrade: { type: gradeType, value } };
                     }
                     return it;
                    });
               setStudents(updateExisting);
               setDisplayedStudents(updateExisting);
               closeModal();
            } else {
               setError('Grade found but ID missing. Please refresh the page.');
            }
          } catch (updateErr) {
               setError(updateErr.response?.data?.detail || 'Failed to update existing grade.');
          }
      } else {
         setError(serverMessage || 'Failed to submit grade. Please check the input and try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen font-sans">
      <div className="max-w-6xl mx-auto">
        {/* Navigation Actions and Header Block */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
            <span className="w-2 h-8 bg-indigo-600 rounded-full"></span>
            Lesson Students
          </h1>
          <div className="flex gap-3">
            <button onClick={() => navigate('/')} className="py-2 px-5 bg-white border border-gray-200 text-gray-600 rounded-2xl font-semibold hover:bg-gray-50 transition-all shadow-sm">← Dashboard</button>
            <button onClick={() => navigate(`/create-lesson`)} className="py-2 px-4 bg-white border border-gray-200 rounded-2xl">Create Lesson</button>
          </div>
        </div>

        {/* AI Intelligent Natural Language Processing Search Component Segment */}
        <div className="bg-white p-5 rounded-3xl shadow-sm border border-gray-100 mb-5">
          <div className="flex items-center gap-3">
            <div className="flex-1 flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-2xl px-4 py-3 focus-within:border-indigo-400 focus-within:ring-2 focus-within:ring-indigo-100 transition-all">
              <span className="text-lg">✨</span>
              <input
                type="text"
                value={aiQuery}
                onChange={(e) => setAiQuery(e.target.value)}
                onKeyDown={handleAiKeyDown}
                placeholder='e.g., "Find students with GPA desc" or "Show students with absenteeism gte 3"'
                disabled={aiLoading}
                className="flex-1 bg-transparent text-sm text-gray-800 placeholder-gray-400 outline-none disabled:opacity-50"
              />
            </div>

            <button
              onClick={handleAiSearch}
              disabled={!aiQuery.trim() || aiLoading}
              className="flex items-center gap-2 py-3 px-5 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {aiLoading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  Searching...
                </>
              ) : (
                <>✨ AI Search</>
              )}
            </button>

            {isFiltered && (
              <button
                onClick={clearAiFilter}
                className="flex items-center gap-1.5 py-3 px-4 bg-white border border-gray-200 text-gray-600 rounded-2xl font-semibold hover:bg-gray-50 transition-all whitespace-nowrap"
                title="Clear filter and show all students"
              >
                ✕ Clear Filter
              </button>
            )}
          </div>

          {aiError && (
            <div className="mt-3 p-3 bg-red-50 border border-red-100 rounded-xl text-xs text-red-600 font-medium">
              {aiError}
            </div>
          )}

          {isFiltered && !aiError && aiResultMeta && (
            <div className="mt-3 flex items-center gap-2 text-xs text-indigo-600 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
              Showing AI-filtered results: {aiResultMeta.count} student{aiResultMeta.count !== 1 ? 's' : ''} found
            </div>
          )}
        </div>

        {/* Primary Student Listings Framework Directory */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
          {loading ? (
            <div className="space-y-4">
              {[1,2,3].map(i => <div key={i} className="h-12 bg-gray-100 animate-pulse rounded-lg"></div>) }
            </div>
          ) : (
            <div>
              {displayedStudents.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  {isFiltered ? 'No students match this AI search.' : 'No students enrolled yet'}
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-indigo-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-indigo-600 uppercase tracking-wider">#</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-indigo-600 uppercase tracking-wider">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-indigo-600 uppercase tracking-wider">Email</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-indigo-600 uppercase tracking-wider">Last Grade</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-indigo-600 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {displayedStudents.map((entry, idx) => {
                        const s = extractStudentInfo(entry);
                        const last = entry?.lastGrade || (entry?.grade_type ? { type: entry.grade_type, value: entry.grade_value } : null);
                        return (
                          <tr key={idx} className="hover:bg-indigo-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{idx + 1}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{s.name}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{s.email || '-'}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{last ? `${last.type}: ${last.value}` : '-'}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                              <button onClick={() => openModal(entry)} className="inline-flex items-center gap-2 py-2 px-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Edit Grade</button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Grade Modification and Submission Overlay Dialog Modal Context */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white rounded-3xl p-8 shadow-2xl border border-gray-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Edit Grade</h3>
            <p className="text-sm text-gray-500 mb-6">Assign a grade (0-100) for the selected assessment type.</p>

            <form onSubmit={handleSubmitGrade} className="space-y-5">
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2 ">Assessment Type</label>
                <select
                 value={gradeType}
                  onChange={(e) => setGradeType(e.target.value)}
                   className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all">
                  <option value="Midterm">Midterm Exam</option>
                  <option value="Final">Final Exam</option>
                  <option value="Quiz">Quiz / Short Test</option>
                  <option value="Homework">Homework / Assignment</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2 ">Grade Value (0-100)</label>
                <input 
                type="number" 
                min="0"
                max="100"
                value={gradeValue} 
                onChange={(e) => setGradeValue(e.target.value)} 
                placeholder="Enter score..."
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all font-bold text-lg" />
              </div>

              {error && (
               <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-xs text-red-600 font-medium">
                    {error}
                    </div>
               )} 

              <div className="flex justify-end gap-3 pt-4">
                <button
                 type="button"
                  onClick={closeModal}
                   className="flex-1 py-3 px-4 bg-white border border-gray-200 text-gray-600 rounded-2xl font-bold hover:bg-gray-50 transition-all"
                   >
                    Cancel
                    </button>
                <button
                 type="submit"
                  disabled={submitting}
                   className="flex-1 py-3 px-4 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition-all disabled:opacity-50"
                   >
                    {submitting ? 'Saving...' : 'Save Grade'}
                    </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default StudentManagement;
