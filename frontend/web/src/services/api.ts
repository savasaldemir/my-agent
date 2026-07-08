import axios from 'axios';

const API_URL = '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authService = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  signup: (username: string, email: string, password: string) =>
    api.post('/auth/signup', { username, email, password }),
  logout: () => api.post('/auth/logout'),
};

export const projectService = {
  getAll: () => api.get('/projects'),
  getById: (id: string) => api.get(`/projects/${id}`),
  create: (data: any) => api.post('/projects', data),
  delete: (id: string) => api.delete(`/projects/${id}`),
};

export const analysisService = {
  analyze: (code: string, language: string, features?: string[]) =>
    api.post('/analysis/analyze', { code, language, features }),
};

export default api;
