import { Router, Request, Response } from 'express';
import axios from 'axios';
import { config } from '../config/environment';

export const authRoutes = Router();

interface LoginRequest {
  username: string;
  password: string;
}

interface SignupRequest {
  username: string;
  email: string;
  password: string;
}

// Login
authRoutes.post('/login', async (req: Request<{}, {}, LoginRequest>, res: Response) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password required' });
    }

    const response = await axios.post(`${config.coreServiceUrl}/api/v1/auth/login`, {
      username,
      password,
    });

    return res.json(response.data);
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return res.status(error.response.status).json(error.response.data);
    }
    return res.status(500).json({ error: 'Authentication failed' });
  }
});

// Signup
authRoutes.post('/signup', async (req: Request<{}, {}, SignupRequest>, res: Response) => {
  try {
    const { username, email, password } = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Username, email, and password required' });
    }

    const response = await axios.post(`${config.coreServiceUrl}/api/v1/auth/register`, {
      username,
      email,
      password,
    });

    return res.status(201).json(response.data);
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return res.status(error.response.status).json(error.response.data);
    }
    return res.status(500).json({ error: 'Signup failed' });
  }
});

// Logout
authRoutes.post('/logout', (_req: Request, res: Response) => {
  return res.json({ message: 'Logged out successfully' });
});
