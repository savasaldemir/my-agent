import { Router, Request, Response } from 'express';
import axios from 'axios';
import { config } from '../config/environment';

export const projectRoutes = Router();

interface CreateProjectRequest {
  name: string;
  description?: string;
  language: string;
  repository_url?: string;
}

// Get all projects
projectRoutes.get('/', async (_req: Request, res: Response) => {
  try {
    const response = await axios.get(`${config.coreServiceUrl}/api/v1/projects`);
    return res.json(response.data);
  } catch (error) {
    return res.status(500).json({ error: 'Failed to fetch projects' });
  }
});

// Create project
projectRoutes.post('/', async (req: Request<{}, {}, CreateProjectRequest>, res: Response) => {
  try {
    const { name, description, language, repository_url } = req.body;

    if (!name || !language) {
      return res.status(400).json({ error: 'Name and language required' });
    }

    const response = await axios.post(`${config.coreServiceUrl}/api/v1/projects`, {
      name,
      description,
      language,
      repository_url,
    });

    return res.status(201).json(response.data);
  } catch (error) {
    return res.status(500).json({ error: 'Failed to create project' });
  }
});

// Get project by ID
projectRoutes.get('/:projectId', async (req: Request, res: Response) => {
  try {
    const { projectId } = req.params;
    const response = await axios.get(`${config.coreServiceUrl}/api/v1/projects/${projectId}`);
    return res.json(response.data);
  } catch (error) {
    return res.status(404).json({ error: 'Project not found' });
  }
});

// Delete project
projectRoutes.delete('/:projectId', async (req: Request, res: Response) => {
  try {
    const { projectId } = req.params;
    await axios.delete(`${config.coreServiceUrl}/api/v1/projects/${projectId}`);
    return res.status(204).send();
  } catch (error) {
    return res.status(500).json({ error: 'Failed to delete project' });
  }
});
