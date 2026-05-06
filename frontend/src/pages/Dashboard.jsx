import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { API_BASE, useAuth } from '../context/AuthContext';

ChartJS.register(ArcElement, Tooltip, Legend);

const STATUS_COLORS = {
  Pending:    '#F59E0B',
  'In Review':'#3B82F6',
  Approved:   '#10B981',
  Closed:     '#6B7280',
};

function StatusBadge({ status }) {
  const cls = {
    Pending:    'badge-warning',
    'In Review':'badge-info',
    Approved:   'badge-success',
    Closed:     'badge-neutral',
  }[status] || 'badge-neutral';
  return <span className={`badge ${cls}`}>{status}</span>;
}

function NavBar({ active }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  return (
    <header className="header">
      <div className="header-brand">
        <span className="brand-icon">📦</span>
        <span className="brand-name">LogiFlow</span>
      </div>
      <nav className="nav-links">
        <Link to="/dashboard" className={`nav-link ${active === 'dashboard' ? 'active' : ''}`}>Dashboard</Link>
        <Link to="/cases"     className={`nav-link ${active === 'cases'     ? 'active' : ''}`}>Cases</Link>
      </nav>
      <div className="header-right">
        <span className="user-pill">👤 {user?.username}</span>
        <button className="btn-logout" onClick={() => { logout(); navigate('/login'); }}>
          Logout
        </button>
      </div>
    </header>
  );
}

export { NavBar, StatusBadge };

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(false);

  useEffect(() => {
    axios.get(`${API_BASE}/dashboard/summary`)
      .then(res => setSummary(res.data))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  const chartData = summary && Object.keys(summary.status_distribution).length > 0
    ? {
        labels: Object.keys(summary.status_distribution),
        datasets: [{
          data: Object.values(summary.status_distribution),
          backgroundColor: Object.keys(summary.status_distribution).map(
            s => STATUS_COLORS[s] || '#9CA3AF'
          ),
          borderWidth: 0,
        }],
      }
    : null;

  return (
    <div className="app-container">
      <NavBar active="dashboard" />

      <div className="page-content">
        <div className="page-heading">
          <h2>Dashboard</h2>
          <p className="page-sub">System overview at a glance</p>
        </div>

        {loading && <div className="loading-state">Loading dashboard...</div>}
        {error   && <div className="empty-state">Failed to load dashboard data. Make sure the backend is running.</div>}

        {summary && (
          <>
            {/* KPI Cards */}
            <div className="kpi-grid">
              <div className="kpi-card">
                <div className="kpi-icon kpi-purple">📁</div>
                <div className="kpi-info">
                  <span className="kpi-value">{summary.total_cases}</span>
                  <span className="kpi-label">Total Cases</span>
                </div>
              </div>
              <div className="kpi-card">
                <div className="kpi-icon kpi-blue">📄</div>
                <div className="kpi-info">
                  <span className="kpi-value">{summary.total_documents}</span>
                  <span className="kpi-label">Documents Uploaded</span>
                </div>
              </div>
              <div className="kpi-card">
                <div className="kpi-icon kpi-yellow">⏳</div>
                <div className="kpi-info">
                  <span className="kpi-value">{summary.pending_review}</span>
                  <span className="kpi-label">Pending Review</span>
                </div>
              </div>
              <div className="kpi-card">
                <div className="kpi-icon kpi-green">✅</div>
                <div className="kpi-info">
                  <span className="kpi-value">{summary.approved}</span>
                  <span className="kpi-label">Approved</span>
                </div>
              </div>
            </div>

            {/* Lower section */}
            <div className="dashboard-lower">
              {/* Recent cases table */}
              <div className="card table-card">
                <div className="card-header">
                  <h3>Recent Cases</h3>
                  <Link to="/cases" className="card-action">View all →</Link>
                </div>
                {summary.recent_cases.length === 0 ? (
                  <div className="empty-state">No cases yet. <Link to="/cases">Create one</Link></div>
                ) : (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Customer</th>
                        <th>Service</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.recent_cases.map(c => (
                        <tr key={c.case_id}>
                          <td><span className="id-pill">#{c.case_id}</span></td>
                          <td>{c.customer}</td>
                          <td>{c.service_type}</td>
                          <td><StatusBadge status={c.status} /></td>
                          <td>
                            <Link to={`/cases/${c.case_id}`} className="table-link">
                              View →
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              {/* Doughnut chart */}
              <div className="card chart-card">
                <div className="card-header">
                  <h3>Status Distribution</h3>
                </div>
                {chartData ? (
                  <div className="chart-wrapper">
                    <Doughnut
                      data={chartData}
                      options={{
                        plugins: { legend: { position: 'bottom', labels: { padding: 16, font: { size: 13 } } } },
                        cutout: '68%',
                        responsive: true,
                        maintainAspectRatio: true,
                      }}
                    />
                  </div>
                ) : (
                  <div className="empty-state">No case data to chart yet.</div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
