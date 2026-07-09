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

export interface WorkspaceTask {
  id: string;
  source_path: string;
  workspace_path: string;
  prompt: string;
  requires_internet: boolean;
  status: string;
  phase: string;
  created_at: string;
  updated_at: string;
  retry_count: number;
  next_retry_at?: string | null;
  last_error?: string | null;
  report_path?: string | null;
  plan_path?: string | null;
  patches_path?: string | null;
  apply_summary_path?: string | null;
}

export interface WorkspaceArtifacts {
  intake_report?: string;
  rebuild_plan?: string;
  generated_patches?: string;
  apply_result?: string;
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

export const workspaceService = {
  listTasks: () => api.get<WorkspaceTask[]>('/workspaces/tasks'),
  intake: (sourcePath: string, prompt: string, requiresInternet: boolean) =>
    api.post<WorkspaceTask>('/workspaces/intake', {
      source_path: sourcePath,
      prompt,
      requires_internet: requiresInternet,
    }),
  processQueue: () => api.post<{ processed: WorkspaceTask[] }>('/workspaces/tasks/process'),
  runTask: (taskId: string) => api.post<WorkspaceTask>(`/workspaces/tasks/${taskId}/run`),
  getTask: (taskId: string) => api.get<WorkspaceTask>(`/workspaces/tasks/${taskId}`),
  getArtifacts: (taskId: string) => api.get<WorkspaceArtifacts>(`/workspaces/tasks/${taskId}/artifacts`),
};

export default api;
