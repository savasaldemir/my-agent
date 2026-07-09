import axios from 'axios';

const API_URL = '/api/v1';

export interface AuthUser {
  id: string;
  username: string;
  email: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: AuthUser;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  language: string;
  repository_url?: string;
  created_at: string;
  updated_at: string;
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((requestConfig) => {
  const token = localStorage.getItem('my-agent-token');
  if (token) {
    requestConfig.headers.Authorization = `Bearer ${token}`;
  }
  return requestConfig;
});

export const authService = {
  login: (username: string, password: string) =>
    api.post<AuthResponse>('/auth/login', { username, password }),
  signup: (username: string, email: string, password: string) =>
    api.post<AuthResponse>('/auth/signup', { username, email, password }),
  logout: () => api.post('/auth/logout'),
};

export const projectService = {
  getAll: () => api.get<Project[]>('/projects'),
  getById: (id: string) => api.get<Project>(`/projects/${id}`),
  create: (data: Omit<Project, 'id' | 'created_at' | 'updated_at'>) => api.post<Project>('/projects', data),
  delete: (id: string) => api.delete(`/projects/${id}`),
};

export const analysisService = {
  analyze: (code: string, language: string, features?: string[]) =>
    api.post('/analysis/analyze', { code, language, features }),
};

export default api;
