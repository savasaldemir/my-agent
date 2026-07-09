import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { Plus, Trash2 } from 'lucide-react';
import { projectService } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { projects, setProjects, setCurrentProject, addProject, removeProject } = useProjectStore();
  const { logout } = useAuthStore();
  const [showCreateForm, setShowCreateForm] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const [newProject, setNewProject] = React.useState({
    name: '',
    language: 'python',
    description: '',
  });

  React.useEffect(() => {
    const loadProjects = async () => {
      setIsLoading(true);
      setError('');
      try {
        const response = await projectService.getAll();
        setProjects(response.data);
      } catch {
        setError('Projects could not be loaded');
      } finally {
        setIsLoading(false);
      }
    };

    void loadProjects();
  }, [setProjects]);

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
    } catch {
      setError('Project could not be deleted');
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">My Agent</h1>
          <button onClick={() => void handleLogout()} className="bg-red-500 text-white px-4 py-2 rounded">
            Logout
          </button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && <div className="mb-4 rounded bg-red-100 p-3 text-red-700">{error}</div>}

        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold">Projects</h2>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-blue-500 text-white px-4 py-2 rounded flex items-center gap-2"
          >
            <Plus size={20} />
            New Project
          </button>
        </div>

        {showCreateForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
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

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
                  className="bg-blue-500 text-white px-4 py-2 rounded w-full mb-2"
                >
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
