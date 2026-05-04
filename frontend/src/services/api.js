// bu dosya tum backend isteklerinin merkezi olacak. tum API istekleri bu dosya uzerinden yapilacak.
// boylece API isteklerini tek bir yerde toplayarak kodun okunabilirligini ve bakim kolayligini artiracagiz.

import axios from 'axios';

const API_URL = 'http://localhost:8000'; // backend'in calistigi adres ve port

const api = axios.create({
     baseURL: API_URL,
});

// Token'ı her istekte eklemek için interceptor
api.interceptors.request.use((config) => {
     const token = localStorage.getItem('token');
     if (token) {
          config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
}, (error) => {
     return Promise.reject(error);
});

// Response hata yonetimi
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

//auth islemleri
export const loginUser = async (username, password) => {
     const params = new URLSearchParams();
     params.append('username', username);
     params.append('password', password);

     const response = await api.post('/auth/login', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
     });
     return response.data; // icinde access_token olacak.
};

export const registerUser = async (username, password, role) => {
     const response = await api.post('/auth/register', { username, password, role });
     return response.data; // kayit olan kullanicinin bilgileri
};

//ders islemleri
export const getLessons = async () => {
     const response = await api.get('/lessons');
     return response.data; // derslerin listesi
};

export const createLesson = async (lessonData) => {
     // lessonData: { bname: "Math", code: "MAT101", teacher_id: 1 }
     const response = await api.post('/lessons', lessonData);
     return response.data; // olusturulan dersin bilgileri
};

export const getTeacherLessons = async (teacherId) => {
     const response = await api.get(`/lessons/teacher/${teacherId}`);
     return response.data; // ogretmenin verdigi derslerin listesi
};

export const getLessonById = async (lessonId) => {
     const response = await api.get(`/lessons/${lessonId}`);
     return response.data; // id'si verilen dersin bilgileri
};

export const updateLesson = async (lessonId, lessonData) => {
     const response = await api.put(`/lessons/${lessonId}`, lessonData);
     return response.data; // guncellenen dersin bilgileri
};

export const deleteLesson = async (lessonId) => {
     const response = await api.delete(`/lessons/${lessonId}`);
     return response.data; // silinen dersin bilgileri
};    

//ogrenci islemleri
export const getStudents = async () => {
     const response = await api.get('/students');
     return response.data; // ogrencilerin listesi
};

export const getAllUsers = async () => {
     const response = await api.get('/students/users/all');
     return response.data; // sistemdeki tum kullanicilarin listesi (admin icin)
};

export const deleteUser = async (userId) => {
     const response = await api.delete(`/students/users/${userId}`);
     return response.data; // silinen kullanicinin bilgileri
};

export const updateUser = async (userId, role) => {
  const response = await api.put(`/students/users/${userId}`, { role });
  return response.data;
};

// ogrencinin kendi notlarini ve transkriptini gormesi icin
export const getMyTranscript = async (userId) => {
     const response = await api.get(`/students/${userId}/transcript`);
     return response.data; // ogrencinin transkripti
};

//ogrencinin derse kayit olmasi(enrollment)
export const enrollInLesson = async (lessonId) => {
     const response = await api.post(`/lessons/${lessonId}/enroll`);
     return response.data; // response after enrollment
};

export const unenrollFromLesson = async (lessonId) => {
  const response = await api.delete(`/lessons/${lessonId}/enroll`);
  return response.data;
};

//ogretmen islemleri
export const getLessonStudents = async (lessonId) => {
     const response = await api.get(`/lessons/${lessonId}/students`);
     return response.data; // derse kayitli ogrencilerin listesi
};

export const submitGrade = async (gradeData) => {
     /* gradeData yapisi:
        { student_id: 1, lesson_id: 2, grade_value: 85, grade_type: "Midterm" }
     */
     const response = await api.post('/grades', gradeData);
     return response.data; // olusturulan grade bilgileri
};

export const updateGrade = async (gradeId, gradeData) => {
     const response = await api.put(`/grades/${gradeId}`, gradeData);
     return response.data; // guncellenen grade bilgileri
};


export const changePassword = async (currentPassword, newPassword) => {
  const response = await api.put('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
  return response.data;
};




export default api;