import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE, useAuth } from '../context/AuthContext';
import { NavBar, StatusBadge } from './Dashboard';

export default function Cases() {
  const [cases, setCases]       = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch]     = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm]         = useState({ customer: '', service_type: '' });
  const [formError, setFormError] = useState('');
  const [creating, setCreating] = useState(false);
  const [loading, setLoading]   = useState(true);

  const fetchCases = () => {
    axios.get(`${API_BASE}/cases/`)
      .then(res => { setCases(res.data); setFiltered(res.data); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchCases(); }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(
      cases.filter(c =>
        c.customer.toLowerCase().includes(q) ||
        String(c.case_id).includes(q) ||
        c.status.toLowerCase().includes(q)
      )
    );
  }, [search, cases]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.customer.trim())     return setFormError('Customer name is required');
    if (!form.service_type.trim()) return setFormError('Service type is required');
    setCreating(true);
    setFormError('');
    try {
      await axios.post(`${API_BASE}/cases/`, form);
      setShowModal(false);
      setForm({ customer: '', service_type: '' });
      fetchCases();
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to create case');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (caseId, customer) => {
    if (!window.confirm(`Delete case #${caseId} (${customer})? This cannot be undone.`)) return;
    try {
      await axios.delete(`${API_BASE}/cases/${caseId}`);
      fetchCases();
    } catch {
      alert('Failed to delete case.');
    }
  };

  return (
    <div className="app-container">
      <NavBar active="cases" />

      <div className="page-content">
        <div className="page-heading">
          <div>
            <h2>Case Management</h2>
            <p className="page-sub">{cases.length} total cases</p>
          </div>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            + New Case
          </button>
        </div>

        <div className="toolbar">
          <input
            className="search-input"
            placeholder="Search by customer, ID, or status…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <div className="card">
          {loading ? (
            <div className="loading-state">Loading cases…</div>
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
                ) : filtered.map(c => (
                  <tr key={c.case_id}>
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
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
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
