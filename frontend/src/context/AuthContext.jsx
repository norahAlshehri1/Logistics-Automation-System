import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

export const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]     = useState(null);
  const [token, setToken]   = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  // Restore session from localStorage on mount
  useEffect(() => {
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const isExpired = payload.exp && Date.now() / 1000 > payload.exp;
        if (isExpired) {
          _clearSession();
        } else {
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          setUser({ username: payload.sub });
        }
      } catch {
        _clearSession();
      }
    }
    setLoading(false);
  }, []);

  // Global 401 interceptor — auto-logout on expired token
  useEffect(() => {
    const id = axios.interceptors.response.use(
      res => res,
      err => {
        if (err.response?.status === 401) {
          _clearSession();
        }
        return Promise.reject(err);
      }
    );
    return () => axios.interceptors.response.eject(id);
  }, []);

  function _clearSession() {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setToken(null);
    setUser(null);
  }

  async function login(username, password) {
    const form = new FormData();
    form.append('username', username);
    form.append('password', password);

    const res = await axios.post(`${API_BASE}/login/`, form);
    const { access_token } = res.data;

    localStorage.setItem('token', access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    setToken(access_token);

    const payload = JSON.parse(atob(access_token.split('.')[1]));
    setUser({ username: payload.sub });
    return res.data;
  }

  function logout() {
    _clearSession();
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
