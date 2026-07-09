import { Router, Request, Response } from 'express';
import axios from 'axios';
import { config } from '../config/environment';

export const analysisRoutes = Router();

interface AnalysisRequest {
  code: string;
  language: string;
  features?: string[];
}

// Analyze code
analysisRoutes.post('/analyze', async (req: Request<{}, {}, AnalysisRequest>, res: Response) => {
  try {
    const { code, language, features } = req.body;

    if (!code || !language) {
      return res.status(400).json({ error: 'Code and language required' });
    }

    const response = await axios.post(`${config.coreServiceUrl}/api/v1/analysis/analyze`, {
      code,
      language,
      features: features || ['quality', 'security', 'performance'],
    });

    return res.json(response.data);
  } catch (error) {
    return res.status(500).json({ error: 'Analysis failed' });
  }
});
