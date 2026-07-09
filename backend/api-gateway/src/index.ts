// API Gateway entry point

import express, { Express } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import 'express-async-errors';

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
app.use(morgan('combined'));
app.use(requestLogger);

// Routes
app.use('/health', healthRoutes);
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/projects', projectRoutes);
app.use('/api/v1/analysis', analysisRoutes);

// Error Handling
app.use(errorHandler);

// 404 Handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not Found' });
});

const PORT = config.port;

app.listen(PORT, config.host, () => {
  logger.info({ host: config.host, port: PORT }, 'API Gateway running');
});

export default app;
