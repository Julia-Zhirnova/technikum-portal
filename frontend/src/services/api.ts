import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
            refresh: refreshToken,
          });
          const newAccessToken = response.data.access;
          localStorage.setItem('access_token', newAccessToken);
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }
    return Promise.reject(error);
  }
);

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface WhoAmIResponse {
  user_id: number;
  email: string;
  full_name: string;
  roles: string[];
}

export interface UserProfile {
  snils: string;
  user: {
    id_user: number;
    email: string;
    last_name: string;
    first_name: string;
    middle_name: string;
    full_name: string;
  };
  group_name: string;
  birth_date: string;
  gender: string;
  birth_place: string;
  phone: string;
  inn: string | null;
  pd_consent: boolean;
  pd_consent_date: string | null;
  status: string;
  photo_path: string | null;
  study_plan: string;
  dual_edu: boolean;
  age: number | null;
  age_status: string | null;
  completion_percentage: number;
  passport: any | null;
  health: any | null;
  military: any | null;
  family: any | null;
  education: any | null;
  profile: any | null;
}

export const authAPI = {
  login: (email: string, password: string) =>
    api.post<LoginResponse>('/token/', { email, password }),
  whoami: () => api.get<WhoAmIResponse>('/whoami/'),
};

export const studentAPI = {
  getProfile: () => api.get<UserProfile>('/student/profile/'),
  updateProfile: (data: any) => api.patch('/student/profile/', data),
};

export const curatorAPI = {
  getGroup: () => api.get('/curator/group/'),
  getStudent: (snils: string) => api.get(`/curator/students/${snils}/`),
};

export const teacherAPI = {
  getStatements: () => api.get('/teacher/statements/'),
};

export default api;


export interface UserProfileData {
  id_user: number;
  email: string;
  last_name: string;
  first_name: string;
  middle_name: string;
  full_name: string;
  roles: string[];
}

export const userAPI = {
  getProfile: () => api.get<UserProfileData>('/user/profile/'),
};
