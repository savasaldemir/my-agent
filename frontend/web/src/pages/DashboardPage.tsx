import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjectStore } from '../store/projectStore';
import { useAuthStore } from '../store/authStore';
import { Plus, Trash2, BarChart3, Settings, LogOut } from 'lucide-react';
import { projectService } from '../services/api';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { projects, setProjects, currentProject, setCurrentProject } = useProjectStore();
  const [showCreateForm, setShowCreateForm] = React.useState(false);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');
  const [newProject, setNewProject] = React.useState({
    name: '',
    language: 'python',
    description: '',
    repository_url: '',
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await projectService.getAll();
      setProjects(response.data);
    } catch (err: any) {
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await projectService.create(newProject);
      setProjects([...projects, response.data]);
      setShowCreateForm(false);
      setNewProject({ name: '', language: 'python', description: '', repository_url: '' });
    } catch (err: any) {
      setError('Failed to create project');
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    try {
      await projectService.delete(projectId);
      setProjects(projects.filter((p) => p.id !== projectId));
    } catch (err: any) {
      setError('Failed to delete project');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">🤖</span>
              </div>
              <h1 className="text-xl font-bold">My Agent</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-gray-600">{user?.username}</span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <LogOut size={20} />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold">Projects</h2>
            <p className="text-gray-600 mt-2">Manage and analyze your projects</p>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 hover:shadow-lg transition"
          >
            <Plus size={20} />
            New Project
          </button>
        </div>

        {/* Create Form */}
        {showCreateForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-8 border border-gray-200">
            <h3 className="text-lg font-semibold mb-4">Create New Project</h3>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Project Name
                  </label>
                  <input
                    type="text"
                    placeholder="My awesome project"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Language
                  </label>
                  <select
                    value={newProject.language}
                    onChange={(e) => setNewProject({ ...newProject, language: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="typescript">TypeScript</option>
                    <option value="go">Go</option>
                    <option value="java">Java</option>
                    <option value="rust">Rust</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  placeholder="Describe your project..."
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 h-24"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Repository URL (Optional)
                </label>
                <input
                  type="url"
                  placeholder="https://github.com/username/repo"
                  value={newProject.repository_url}
                  onChange={(e) => setNewProject({ ...newProject, repository_url: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition font-medium"
                >
                  Create Project
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 transition font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Projects Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
            <p className="text-gray-600 mt-4">Loading projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center border border-gray-200">
            <div className="text-5xl mb-4">📭</div>
            <p className="text-gray-600 text-lg mb-6">No projects yet</p>
            <p className="text-gray-500 mb-6">Create your first project to get started with analysis</p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition"
            >
              Create First Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition border border-gray-200 overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">{project.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">{project.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 mb-4">
                    <span className="inline-block px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full">
                      {project.language}
                    </span>
                  </div>

                  {project.repository_url && (
                    <p className="text-sm text-gray-500 mb-4 truncate">
                      {project.repository_url}
                    </p>
                  )}

                  <div className="flex gap-2 pt-4 border-t">
                    <button
                      onClick={() => setCurrentProject(project)}
                      className="flex-1 bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition font-medium flex items-center justify-center gap-2"
                    >
                      <BarChart3 size={16} />
                      Analyze
                    </button>
                    <button
                      onClick={() => handleDeleteProject(project.id)}
                      className="flex-1 bg-red-50 text-red-600 py-2 rounded-lg hover:bg-red-100 transition font-medium flex items-center justify-center gap-2"
                    >
                      <Trash2 size={16} />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
