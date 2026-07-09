import { create } from 'zustand';
import { authService } from '../services/api';

interface AuthState {
  isAuthenticated: boolean;
  user: null | { id: string; username: string; email: string };
  token: null | string;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const storedToken = localStorage.getItem('my-agent-token');
const storedUser = localStorage.getItem('my-agent-user');
const parsedUser = storedUser ? (JSON.parse(storedUser) as { id: string; username: string; email: string }) : null;

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: Boolean(storedToken),
  user: parsedUser,
  token: storedToken,
  login: async (username: string, password: string) => {
    const response = await authService.login(username, password);
    const data = response.data;

    localStorage.setItem('my-agent-token', data.access_token);
    localStorage.setItem('my-agent-user', JSON.stringify(data.user));

    set({
      isAuthenticated: true,
      user: {
        id: data.user.id,
        username: data.user.username,
        email: data.user.email,
      },
      token: data.access_token,
    });
  },
  logout: async () => {
    await authService.logout();
    localStorage.removeItem('my-agent-token');
    localStorage.removeItem('my-agent-user');

    set({
      isAuthenticated: false,
      user: null,
      token: null,
    });
  },
}));
