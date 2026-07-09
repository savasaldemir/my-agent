import { Router, Request, Response } from 'express';

export const healthRoutes = Router();

healthRoutes.get('/', (_req: Request, res: Response) => {
  return res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

healthRoutes.get('/ready', (_req: Request, res: Response) => {
  return res.json({
    status: 'ready',
  });
});
