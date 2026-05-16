import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { API_BASE, useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { NavBar, StatusBadge } from './Dashboard';
import { TableSkeleton } from '../components/Skeleton';

const STATUS_FILTER_OPTIONS = ['All', 'Pending', 'In Review', 'Approved', 'Closed'];

export default function Cases() {
  const [cases, setCases]       = useState([]);
  const [search, setSearch]     = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm]         = useState({ customer: '', service_type: '' });
  const [formError, setFormError] = useState('');
  const [creating, setCreating] = useState(false);
  const [loading, setLoading]   = useState(true);

  const { user } = useAuth();
  const toast    = useToast();
  const isAdmin  = (user?.role || '').toLowerCase() === 'admin';

  const fetchCases = () => {
    axios.get(`${API_BASE}/cases/`)
      .then(res => setCases(res.data))
      .catch(() => toast.error('Failed to load cases'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchCases(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Debounce search input (300ms) — avoids re-filtering on every keystroke
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search.toLowerCase()), 300);
    return () => clearTimeout(t);
  }, [search]);

  const filtered = useMemo(() => {
    return cases.filter(c => {
      const matchesText =
        c.customer.toLowerCase().includes(debouncedSearch) ||
        String(c.case_id).includes(debouncedSearch) ||
        c.status.toLowerCase().includes(debouncedSearch);
      const matchesStatus = statusFilter === 'All' || c.status === statusFilter;
      return matchesText && matchesStatus;
    });
  }, [cases, debouncedSearch, statusFilter]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.customer.trim())     { setFormError('Customer name is required'); return; }
    if (!form.service_type.trim()) { setFormError('Service type is required'); return; }
    setCreating(true);
    setFormError('');
    try {
      await axios.post(`${API_BASE}/cases/`, form);
      setShowModal(false);
      setForm({ customer: '', service_type: '' });
      toast.success(`Case created for ${form.customer}`);
      fetchCases();
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to create case');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (caseId, customer) => {
    if (!isAdmin) {
      toast.warning('Only admins can delete cases');
      return;
    }
    if (!window.confirm(`Delete case #${caseId} (${customer})? This cannot be undone.`)) return;
    try {
      await axios.delete(`${API_BASE}/cases/${caseId}`);
      toast.success(`Case #${caseId} deleted`);
      fetchCases();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete case');
    }
  };

  return (
    <div className="app-container">
      <NavBar active="cases" />

      <div className="page-content page-fade-in">
        <div className="page-heading">
          <div>
            <h2>Case Management</h2>
            <p className="page-sub">
              {loading ? 'Loading…' :
                `${cases.length} total cases · ${filtered.length} shown`}
            </p>
          </div>
          <button className="btn-primary btn-glow" onClick={() => setShowModal(true)}>
            + New Case
          </button>
        </div>

        <div className="toolbar">
          <input
            className="search-input"
            placeholder="🔎  Search by customer, ID, or status…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <select
            className="status-select toolbar-filter"
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
          >
            {STATUS_FILTER_OPTIONS.map(s => (
              <option key={s} value={s}>{s === 'All' ? 'All statuses' : s}</option>
            ))}
          </select>
        </div>

        <div className="card card-fade-in">
          {loading ? (
            <TableSkeleton rows={6} cols={6} />
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Customer</th>
                  <th>Service Type</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="empty-cell">
                      {search ? 'No cases match your search.' : 'No cases yet. Create one!'}
                    </td>
                  </tr>
                ) : filtered.map((c, i) => (
                  <tr key={c.case_id} className="row-fade-in" style={{ animationDelay: `${i * 30}ms` }}>
                    <td><span className="id-pill">#{c.case_id}</span></td>
                    <td className="fw-medium">{c.customer}</td>
                    <td>{c.service_type}</td>
                    <td><StatusBadge status={c.status} /></td>
                    <td className="text-muted">
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : '—'}
                    </td>
                    <td className="action-cell">
                      <Link to={`/cases/${c.case_id}`} className="btn-sm btn-view">
                        View
                      </Link>
                      <button
                        className="btn-sm btn-delete"
                        onClick={() => handleDelete(c.case_id, c.customer)}
                        disabled={!isAdmin}
                        title={isAdmin ? 'Delete this case' : 'Admin only'}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Create Case Modal */}
      {showModal && (
        <div className="modal-overlay modal-overlay-animated" onClick={() => setShowModal(false)}>
          <div className="modal modal-animated" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Case</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            </div>
            {formError && <div className="alert alert-error">{formError}</div>}
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Customer Name</label>
                <input
                  type="text"
                  placeholder="e.g. Aramex Saudi Arabia"
                  value={form.customer}
                  onChange={e => setForm(p => ({ ...p, customer: e.target.value }))}
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Service Type</label>
                <input
                  type="text"
                  placeholder="e.g. Air Freight, Sea Freight, Road"
                  value={form.service_type}
                  onChange={e => setForm(p => ({ ...p, service_type: e.target.value }))}
                />
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={creating}>
                  {creating ? 'Creating…' : 'Create Case'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
