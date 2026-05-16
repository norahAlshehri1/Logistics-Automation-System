/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useEffect, useState } from 'react';

const ToastContext = createContext(null);

let _id = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismiss = useCallback((id) => {
    setToasts(t => t.filter(x => x.id !== id));
  }, []);

  const push = useCallback((message, type = 'info', ttl = 3500) => {
    const id = ++_id;
    setToasts(t => [...t, { id, message, type }]);
    if (ttl > 0) setTimeout(() => dismiss(id), ttl);
    return id;
  }, [dismiss]);

  const api = {
    success: (m, ttl) => push(m, 'success', ttl),
    error:   (m, ttl) => push(m, 'error', ttl ?? 5000),
    info:    (m, ttl) => push(m, 'info', ttl),
    warning: (m, ttl) => push(m, 'warning', ttl),
    dismiss,
  };

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="toast-stack" role="region" aria-label="Notifications">
        {toasts.map(t => (
          <Toast key={t.id} toast={t} onClose={() => dismiss(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function Toast({ toast, onClose }) {
  const [leaving, setLeaving] = useState(false);

  // Coordinate slide-out animation before unmount
  useEffect(() => {
    const t = setTimeout(() => setLeaving(false), 50);
    return () => clearTimeout(t);
  }, []);

  const close = () => {
    setLeaving(true);
    setTimeout(onClose, 220);
  };

  const icon = {
    success: '✓',
    error:   '✕',
    warning: '!',
    info:    'i',
  }[toast.type];

  return (
    <div className={`toast toast-${toast.type} ${leaving ? 'toast-leave' : ''}`}>
      <span className="toast-icon">{icon}</span>
      <span className="toast-msg">{toast.message}</span>
      <button className="toast-close" onClick={close} aria-label="Dismiss">×</button>
    </div>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside ToastProvider');
  return ctx;
}
