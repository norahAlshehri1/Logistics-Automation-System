/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

export const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]     = useState(null);
  const [token, setToken]   = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  // Restore session from localStorage on mount, then fetch /me/ for the role.
  useEffect(() => {
    async function restore() {
      if (!token) { setLoading(false); return; }
      try {
        const b64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
        const padded = b64 + '==='.slice((b64.length + 3) % 4);
        const payload = JSON.parse(atob(padded));
        const isExpired = payload.exp && Date.now() / 1000 > payload.exp;
        if (isExpired) { _clearSession(); setLoading(false); return; }
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        setUser({ username: payload.sub });
        try {
          const res = await axios.get(`${API_BASE}/me/`);
          setUser(res.data);  // { id, username, role }
        } catch { /* keep partial user */ }
      } catch {
        _clearSession();
      } finally {
        setLoading(false);
      }
    }
    restore();
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

    try {
      const me = await axios.get(`${API_BASE}/me/`);
      setUser(me.data);
    } catch {
      const b64 = access_token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = b64 + '==='.slice((b64.length + 3) % 4);
      const payload = JSON.parse(atob(padded));
      setUser({ username: payload.sub });
    }
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
