import { create } from 'zustand';

interface AuthState {
  isAuthenticated: boolean;
  user: null | { id: string; username: string };
  token: null | string;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  token: null,
  login: async (username: string, password: string) => {
    // TODO: Implement login logic
    set({
      isAuthenticated: true,
      user: { id: 'user_123', username },
      token: 'mock-token',
    });
  },
  logout: () => {
    set({
      isAuthenticated: false,
      user: null,
      token: null,
    });
  },
}));
