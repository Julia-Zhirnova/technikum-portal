import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
});

// Перехватчик запросов: добавляем токен и активную роль
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  const activeRole = localStorage.getItem('activeRole');
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Важно: передаем роль в заголовке, если она есть
  if (activeRole) {
    config.headers['X-Active-Role'] = activeRole;
  }
  
  return config;
});

// Перехватчик ответов
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Если токен истек (401), идем на логин
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // ВАЖНОЕ ИСПРАВЛЕНИЕ: Не сбрасываем роль при 403!
    // 403 может быть временным или специфичным для эндпоинта.
    // Сброс роли здесь вызывает бесконечный редирект-луп.
    if (error.response?.status === 403) {
      console.warn('403 Forbidden:', error.config?.url);
      // Можно добавить логику показа сообщения пользователю, но не редирект
    }

    return Promise.reject(error);
  }
);

export default api;
