import axios from 'axios';

// Baseline configurations targeting the backend microservice architecture gateway
const API_URL = 'http://localhost:8000';

const api = axios.create({
     baseURL: API_URL,
});

/**
 * Request Interceptor.
 * Automatically injects the signed Bearer JWT token claim from localStorage 
 * into the Authorization headers profile of all outgoing corporate API streams.
 */
api.interceptors.request.use((config) => {
     const token = localStorage.getItem('token');
     if (token) {
          config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
}, (error) => {
     return Promise.reject(error);
});

/**
 * Response Interceptor.
 * Implements a global error catching system. If a 401 Unauthorized status is intercepted, 
 * it programmatically wipes local cache identifiers and forcefully redirects sessions back to the gateway.
 */
api.interceptors.response.use(
     (response) => response,
     (error) => {
          if (error.response?.status === 401) {
               localStorage.removeItem('token');
               localStorage.removeItem('user');
               window.location.href = '/login';
          }
          return Promise.reject(error);
     }
);

// ==========================================
// AUTHENTICATION INTERFACE SERVICES
// ==========================================

export const loginUser = async (username, password) => {
     const params = new URLSearchParams();
     params.append('username', username);
     params.append('password', password);

     // Identity operational verification using URL encoded form data protocols mapping
     const response = await api.post('/auth/login', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
     });
     return response.data; 
};

export const registerUser = async (username, password, role) => {
     const response = await api.post('/auth/register', { username, password, role });
     return response.data; 
};

export const changePassword = async (currentPassword, newPassword) => {
     const response = await api.put('/auth/change-password', {
       current_password: currentPassword,
       new_password: newPassword,
     });
     return response.data;
};

// ==========================================
// COURSE MANAGEMENT INTERFACE SERVICES
// ==========================================

export const getLessons = async () => {
     const response = await api.get('/lessons');
     return response.data; 
};

export const createLesson = async (lessonData) => {
     const response = await api.post('/lessons', lessonData);
     return response.data; 
};

export const getTeacherLessons = async (teacherId) => {
     const response = await api.get(`/lessons/teacher/${teacherId}`);
     return response.data; 
};

export const getLessonById = async (lessonId) => {
     const response = await api.get(`/lessons/${lessonId}`);
     return response.data; 
};

export const updateLesson = async (lessonId, lessonData) => {
     const response = await api.put(`/lessons/${lessonId}`, lessonData);
     return response.data; 
};

export const deleteLesson = async (lessonId) => {
     const response = await api.delete(`/lessons/${lessonId}`);
     return response.data; 
};    

// ==========================================
// STUDENT PROFILE INTERFACE SERVICES
// ==========================================

export const getStudents = async () => {
     const response = await api.get('/students');
     return response.data; 
};

export const getAllUsers = async () => {
     const response = await api.get('/students/users/all');
     return response.data; 
};

export const deleteUser = async (userId) => {
     const response = await api.delete(`/students/users/${userId}`);
     return response.data; 
};

export const updateUser = async (userId, role) => {
     const response = await api.put(`/students/users/${userId}`, { role });
     return response.data;
};

export const getMyTranscript = async (userId) => {
     const response = await api.get(`/students/${userId}/transcript`);
     return response.data; 
};

export const enrollInLesson = async (lessonId) => {
     const response = await api.post(`/lessons/${lessonId}/enroll`);
     return response.data; 
};

export const unenrollFromLesson = async (lessonId) => {
     const response = await api.delete(`/lessons/${lessonId}/enroll`);
     return response.data;
};

// ==========================================
// EVALUATION GRADE INTERFACE SERVICES
// ==========================================

export const getLessonStudents = async (lessonId) => {
     const response = await api.get(`/lessons/${lessonId}/students`);
     return response.data; 
};

export const submitGrade = async (gradeData) => {
     const response = await api.post('/grades', gradeData);
     return response.data; 
};

export const updateGrade = async (gradeId, gradeData) => {
     const response = await api.put(`/grades/${gradeId}`, gradeData);
     return response.data; 
};

// ==========================================
// AI COGNITIVE COMPUTING LAYER SERVICES
// ==========================================

export const getStudentComment = async (studentId) => {
     const response = await api.get(`/students/${studentId}/comment`);
     return response.data; 
};

export const getStudentRecommendations = async (studentId) => {
     const response = await api.get(`/students/${studentId}/recommendations`);
     return response.data; 
};

export const executeAiQuery = async (queryText) => {
     const response = await api.post('/students/ai-query', { query: queryText });
     return response.data; 
};

export const sendChatBotMessage = async (messageText) => {
     const response = await api.post('/students/chat', { message: messageText });
     return response.data; 
};

export default api;