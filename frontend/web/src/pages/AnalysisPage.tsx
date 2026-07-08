import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjectStore } from '../store/projectStore';
import { useAuthStore } from '../store/authStore';
import { ArrowLeft, Send } from 'lucide-react';
import { analysisService } from '../services/api';

export const AnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentProject, setCurrentProject } = useProjectStore();
  const { user } = useAuthStore();
  const [code, setCode] = React.useState('');
  const [fileName, setFileName] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [results, setResults] = React.useState<any>(null);
  const [error, setError] = React.useState('');

  if (!currentProject) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 text-lg mb-4">No project selected</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code || !fileName) {
      setError('Please provide file name and code');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const response = await analysisService.analyze(
        code,
        currentProject.language,
        ['quality', 'security', 'performance']
      );
      setResults(response.data);
    } catch (err: any) {
      setError('Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  setCurrentProject(null);
                  navigate('/dashboard');
                }}
                className="flex items-center gap-2 text-blue-500 hover:text-blue-600"
              >
                <ArrowLeft size={20} />
                Back
              </button>
              <h1 className="text-xl font-bold">{currentProject.name}</h1>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div>
            <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
              <h2 className="text-xl font-bold mb-4">Code Analysis</h2>
              
              {error && (
                <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <form onSubmit={handleAnalyze} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    File Name
                  </label>
                  <input
                    type="text"
                    placeholder="main.py, app.js, etc."
                    value={fileName}
                    onChange={(e) => setFileName(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Code ({currentProject.language})
                  </label>
                  <textarea
                    placeholder="Paste your code here..."
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm h-96"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-lg hover:shadow-lg transition font-medium flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <Send size={20} />
                  {loading ? 'Analyzing...' : 'Analyze Code'}
                </button>
              </form>
            </div>
          </div>

          {/* Results Section */}
          <div>
            {results ? (
              <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
                <h2 className="text-xl font-bold mb-4">Analysis Results</h2>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    {results.quality_score && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600">Quality</p>
                        <p className="text-2xl font-bold text-blue-600">{results.quality_score}</p>
                      </div>
                    )}
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Issues</p>
                      <p className="text-2xl font-bold text-purple-600">{results.total_issues}</p>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Status</p>
                      <p className="text-2xl font-bold text-green-600">✓</p>
                    </div>
                  </div>

                  {results.issues && results.issues.length > 0 && (
                    <div className="mt-6">
                      <h3 className="font-semibold mb-3">Found Issues:</h3>
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {results.issues.map((issue: any, idx: number) => (
                          <div key={idx} className="border-l-4 border-red-500 bg-red-50 p-3 rounded">
                            <p className="font-medium text-red-900">Line {issue.line}</p>
                            <p className="text-sm text-red-800">{issue.message}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-6 border border-gray-200 text-center py-12">
                <div className="text-5xl mb-4">📊</div>
                <p className="text-gray-600">Analysis results will appear here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
