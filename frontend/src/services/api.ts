// src/services/api.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:80';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tutor_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('tutor_token');
      localStorage.removeItem('tutor_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data: { login: string; password: string; first_name: string }) =>
    api.post('/api/auth/register', data),

  login: (data: { login: string; password: string }) =>
    api.post('/api/auth/login', data),

  logout: () => {
    localStorage.removeItem('tutor_token');
    localStorage.removeItem('tutor_user');
  },
};

export const tutorAPI = {
  getStats: (telegramId: number) =>
    api.get(`/api/tutors/${telegramId}/stats`),

  getStudents: (telegramId: number) =>
    api.get(`/api/tutors/${telegramId}/students`),

  getLessons: (telegramId: number) =>
    api.get(`/api/tutors/${telegramId}/lessons`),

  getInvites: (telegramId: number) =>
    api.get(`/api/tutors/${telegramId}/invites`),

  createInvite: (telegramId: number, studentName: string) =>
    api.post(`/api/tutors/${telegramId}/invites`, { student_name: studentName }),
};