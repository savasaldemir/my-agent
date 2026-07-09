import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { FolderUp, Globe, Play, Plus, RefreshCw, ShieldCheck, Trash2 } from 'lucide-react';
import { projectService, workspaceService } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    projects,
    workspaceTasks,
    setProjects,
    setCurrentProject,
    addProject,
    removeProject,
    setWorkspaceTasks,
    upsertWorkspaceTask,
  } = useProjectStore();
  const { logout } = useAuthStore();
  const [showCreateForm, setShowCreateForm] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);
  const [isQueueRunning, setIsQueueRunning] = React.useState(false);
  const [error, setError] = React.useState('');
  const [successMessage, setSuccessMessage] = React.useState('');
  const [newProject, setNewProject] = React.useState({
    name: '',
    language: 'python',
    description: '',
  });
  const [intakeForm, setIntakeForm] = React.useState({
    sourcePath: '',
    prompt: 'Projeyi güvenli, modern ve çalıştırılabilir hale getir.',
    requiresInternet: false,
  });

  React.useEffect(() => {
    const loadDashboard = async () => {
      setIsLoading(true);
      setError('');
      try {
        const [projectsResponse, tasksResponse] = await Promise.all([
          projectService.getAll(),
          workspaceService.listTasks(),
        ]);
        setProjects(projectsResponse.data);
        setWorkspaceTasks(tasksResponse.data);
      } catch {
        setError('Dashboard verileri yüklenemedi');
      } finally {
        setIsLoading(false);
      }
    };

    void loadDashboard();
  }, [setProjects, setWorkspaceTasks]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const response = await projectService.create({
        name: newProject.name,
        language: newProject.language,
        description: newProject.description || undefined,
      });
      addProject(response.data);
      setSuccessMessage('Project created successfully');
    } catch {
      setError('Project could not be created');
      return;
    }

    setShowCreateForm(false);
    setNewProject({ name: '', language: 'python', description: '' });
  };

  const handleDeleteProject = async (projectId: string) => {
    setError('');
    try {
      await projectService.delete(projectId);
      removeProject(projectId);
      setSuccessMessage('Project deleted successfully');
    } catch {
      setError('Project could not be deleted');
    }
  };

  const handleIntakeSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setSuccessMessage('');

    if (!intakeForm.sourcePath.trim()) {
      setError('Source path is required');
      return;
    }

    try {
      const response = await workspaceService.intake(
        intakeForm.sourcePath,
        intakeForm.prompt,
        intakeForm.requiresInternet,
      );
      upsertWorkspaceTask(response.data);
      setSuccessMessage(response.data.status === 'pending' ? 'Task queued successfully' : 'Intake completed successfully');
    } catch {
      setError('Workspace intake could not be started');
    }
  };

  const handleProcessQueue = async () => {
    setIsQueueRunning(true);
    setError('');
    setSuccessMessage('');
    try {
      const response = await workspaceService.processQueue();
      response.data.processed.forEach((task) => upsertWorkspaceTask(task));
      setSuccessMessage(response.data.processed.length > 0 ? 'Queued tasks processed' : 'No queued task was ready');
    } catch {
      setError('Queue processing failed');
    } finally {
      setIsQueueRunning(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-slate-950 text-white shadow-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">My Agent Workbench</h1>
            <p className="text-sm text-slate-300">Project intake, secure rebuild queue, and runtime control</p>
          </div>
          <button onClick={() => void handleLogout()} className="rounded bg-rose-500 px-4 py-2 text-white">
            Logout
          </button>
        </div>
      </nav>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {error && <div className="mb-4 rounded bg-red-100 p-3 text-red-700">{error}</div>}
        {successMessage && <div className="mb-4 rounded bg-emerald-100 p-3 text-emerald-800">{successMessage}</div>}

        <div className="mb-8 grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="rounded-2xl bg-slate-950 p-6 text-white shadow-xl">
            <div className="mb-6 flex items-center gap-3">
              <ShieldCheck className="h-6 w-6 text-emerald-400" />
              <div>
                <h2 className="text-2xl font-bold">Secure Intake Pipeline</h2>
                <p className="text-sm text-slate-300">Import an existing project, queue it if internet is required, and keep rebuilding from a safe workspace.</p>
              </div>
            </div>

            <form onSubmit={handleIntakeSubmit} className="space-y-4">
              <input
                type="text"
                placeholder="C:\\Projects\\your-app"
                value={intakeForm.sourcePath}
                onChange={(event) => setIntakeForm({ ...intakeForm, sourcePath: event.target.value })}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-white"
              />
              <textarea
                value={intakeForm.prompt}
                onChange={(event) => setIntakeForm({ ...intakeForm, prompt: event.target.value })}
                className="min-h-32 w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-white"
                placeholder="How should the imported project be rebuilt?"
              />
              <label className="flex items-center gap-3 text-sm text-slate-200">
                <input
                  type="checkbox"
                  checked={intakeForm.requiresInternet}
                  onChange={(event) => setIntakeForm({ ...intakeForm, requiresInternet: event.target.checked })}
                />
                Retry later if internet is unavailable
              </label>
              <div className="flex flex-wrap gap-3">
                <button type="submit" className="inline-flex items-center gap-2 rounded bg-cyan-500 px-4 py-2 font-semibold text-slate-950">
                  <FolderUp size={18} />
                  Start Intake
                </button>
                <button
                  type="button"
                  onClick={() => void handleProcessQueue()}
                  disabled={isQueueRunning}
                  className="inline-flex items-center gap-2 rounded border border-slate-600 px-4 py-2 font-semibold text-white"
                >
                  <RefreshCw size={18} className={isQueueRunning ? 'animate-spin' : ''} />
                  Process Queue
                </button>
                <a href="http://127.0.0.1:3000" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded border border-slate-600 px-4 py-2 font-semibold text-white">
                  <Globe size={18} />
                  Open App
                </a>
              </div>
            </form>
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-lg">
            <h2 className="mb-4 text-xl font-bold text-slate-900">Queued Workspaces</h2>
            <div className="space-y-3">
              {workspaceTasks.length === 0 ? (
                <div className="rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500">No intake task yet.</div>
              ) : (
                workspaceTasks.map((task) => (
                  <div key={task.id} className="rounded-xl border border-slate-200 p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-semibold text-slate-900">{task.source_path}</p>
                        <p className="text-sm text-slate-500">Workspace: {task.workspace_path}</p>
                      </div>
                      <span className="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
                        {task.status}
                      </span>
                    </div>
                    <p className="mt-3 text-sm text-slate-600">Retries: {task.retry_count}{task.last_error ? ` • ${task.last_error}` : ''}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-3xl font-bold">Projects</h2>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="flex items-center gap-2 rounded bg-blue-500 px-4 py-2 text-white"
          >
            <Plus size={20} />
            New Project
          </button>
        </div>

        {showCreateForm && (
          <div className="mb-6 rounded-lg bg-white p-6 shadow">
            <form onSubmit={handleCreateProject} className="space-y-4">
              <input
                type="text"
                placeholder="Project name"
                value={newProject.name}
                onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg"
                required
              />
              <select
                value={newProject.language}
                onChange={(e) => setNewProject({ ...newProject, language: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="go">Go</option>
                <option value="java">Java</option>
              </select>
              <textarea
                placeholder="Description"
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg"
              />
              <div className="flex gap-4">
                <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {isLoading && (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-500 text-lg">Loading projects...</p>
            </div>
          )}

          {projects.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-500 text-lg">No projects yet. Create one to get started!</p>
            </div>
          ) : (
            projects.map((project) => (
              <div key={project.id} className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-bold mb-2">{project.name}</h3>
                <p className="text-gray-600 text-sm mb-2">{project.description}</p>
                <p className="text-blue-600 font-semibold mb-4">{project.language}</p>
                <button
                  onClick={() => setCurrentProject(project)}
                  className="mb-2 flex w-full items-center justify-center gap-2 rounded bg-blue-500 px-4 py-2 text-white"
                >
                  <Play size={18} />
                  View
                </button>
                <button
                  onClick={() => void handleDeleteProject(project.id)}
                  className="bg-red-500 text-white px-4 py-2 rounded w-full flex items-center justify-center gap-2"
                >
                  <Trash2 size={18} />
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
