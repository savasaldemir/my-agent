import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { Plus, Trash2 } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { projects, currentProject, setCurrentProject } = useProjectStore();
  const [showCreateForm, setShowCreateForm] = React.useState(false);
  const [newProject, setNewProject] = React.useState({
    name: '',
    language: 'python',
    description: '',
  });

  const handleCreateProject = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Call API to create project
    setShowCreateForm(false);
    setNewProject({ name: '', language: 'python', description: '' });
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">My Agent</h1>
          <button className="bg-red-500 text-white px-4 py-2 rounded">Logout</button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
