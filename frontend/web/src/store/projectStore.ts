import { create } from 'zustand';

import type { WorkspaceTask } from '../services/api';

interface Project {
  id: string;
  name: string;
  description?: string;
  language: string;
  repository_url?: string;
  created_at: string;
  updated_at: string;
}

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  workspaceTasks: WorkspaceTask[];
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  addProject: (project: Project) => void;
  removeProject: (projectId: string) => void;
  setWorkspaceTasks: (tasks: WorkspaceTask[]) => void;
  upsertWorkspaceTask: (task: WorkspaceTask) => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  currentProject: null,
  workspaceTasks: [],
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (project) => set({ currentProject: project }),
  addProject: (project) =>
    set((state) => ({
      projects: [...state.projects, project],
    })),
  removeProject: (projectId) =>
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== projectId),
    })),
  setWorkspaceTasks: (tasks) => set({ workspaceTasks: tasks }),
  upsertWorkspaceTask: (task) =>
    set((state) => {
      const existing = state.workspaceTasks.find((item) => item.id === task.id);
      if (!existing) {
        return { workspaceTasks: [task, ...state.workspaceTasks] };
      }

      return {
        workspaceTasks: state.workspaceTasks.map((item) => (item.id === task.id ? task : item)),
      };
    }),
}));
