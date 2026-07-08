import { Router, Request, Response } from 'express';

export const healthRoutes = Router();

healthRoutes.get('/', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

healthRoutes.get('/ready', (req: Request, res: Response) => {
  res.json({
    status: 'ready',
  });
});
