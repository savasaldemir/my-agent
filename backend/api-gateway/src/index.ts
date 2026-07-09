// API Gateway entry point

import express, { Express } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import 'express-async-errors';
import path from 'path';
import { fileURLToPath } from 'url';

import { config } from './config/environment';
import { errorHandler } from './middleware/errorHandler';
import { getLogger, requestLogger } from './middleware/logger';
import { authRoutes } from './routes/auth';
import { projectRoutes } from './routes/projects';
import { analysisRoutes } from './routes/analysis';
import { healthRoutes } from './routes/health';

const app: Express = express();
const logger = getLogger();
const allowCredentials = !config.corsOrigins.includes('*');
const currentFile = fileURLToPath(import.meta.url);
const currentDir = path.dirname(currentFile);
const frontendDistDir = path.resolve(currentDir, '../../../../frontend/web/dist');

// Security Middleware
app.use(helmet());
app.use(cors({
  origin: config.corsOrigins,
  credentials: allowCredentials,
}));

// Body Parser
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ limit: '10mb', extended: true }));

// Logging
app.use(requestLogger);

// Routes
app.use('/health', healthRoutes);
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/projects', projectRoutes);
app.use('/api/v1/analysis', analysisRoutes);

// Static frontend for the packaged AGENT application
app.use(express.static(frontendDistDir));

app.get('*', (req, res, next) => {
  if (req.path.startsWith('/api/') || req.path.startsWith('/health')) {
    return next();
  }

  return res.sendFile(path.join(frontendDistDir, 'index.html'));
});

// Error Handling
app.use(errorHandler);

// 404 Handler
app.use((_req, res) => {
  res.status(404).json({ error: 'Not Found' });
});

const PORT = config.port;

app.listen(PORT, config.host, () => {
  logger.info({ host: config.host, port: PORT }, 'API Gateway running');
});

export default app;
