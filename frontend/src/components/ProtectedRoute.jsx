import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="boot-screen">
        <div className="boot-brand">
          <span className="boot-icon">📦</span>
          <span className="boot-name">LogiFlow</span>
        </div>
        <div className="spinner" />
        <p className="boot-sub">Restoring session…</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
