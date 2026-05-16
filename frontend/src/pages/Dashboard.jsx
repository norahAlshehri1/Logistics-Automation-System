import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js';
import { API_BASE, useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../context/ToastContext';
import { KpiSkeleton, TableSkeleton, ChartSkeleton } from '../components/Skeleton';

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const STATUS_COLORS = {
  Pending:    '#F59E0B',
  'In Review':'#3B82F6',
  Approved:   '#10B981',
  Closed:     '#6B7280',
};

const ROLE_LABEL = {
  admin:  { text: 'Admin',  className: 'role-admin'  },
  staff:  { text: 'Staff',  className: 'role-staff'  },
  viewer: { text: 'Viewer', className: 'role-viewer' },
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

function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button
      className="theme-toggle"
      onClick={toggle}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      <span className={`theme-icon ${theme === 'dark' ? 'show' : ''}`}>🌙</span>
      <span className={`theme-icon ${theme === 'light' ? 'show' : ''}`}>☀️</span>
    </button>
  );
}

function NavBar({ active }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const role = (user?.role || 'staff').toLowerCase();
  const roleInfo = ROLE_LABEL[role] || ROLE_LABEL.staff;

  return (
    <header className="header">
      <div className="header-brand">
        <span className="brand-icon">📦</span>
        <span className="brand-name">LogiFlow</span>
      </div>
      <nav className="nav-links">
        <Link to="/dashboard" className={`nav-link ${active === 'dashboard' ? 'active' : ''}`}>
          Dashboard
        </Link>
        <Link to="/cases" className={`nav-link ${active === 'cases' ? 'active' : ''}`}>
          Cases
        </Link>
      </nav>
      <div className="header-right">
        <ThemeToggle />
        <div className="user-pill">
          <span className="user-avatar">{user?.username?.[0]?.toUpperCase() ?? '?'}</span>
          <div className="user-meta">
            <span className="user-name">{user?.username}</span>
            <span className={`role-chip ${roleInfo.className}`}>{roleInfo.text}</span>
          </div>
        </div>
        <button
          className="btn-logout"
          onClick={() => { logout(); toast.info('Signed out'); navigate('/login'); }}
        >
          Logout
        </button>
      </div>
    </header>
  );
}

export { NavBar, StatusBadge };

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [kpi, setKpi]         = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    Promise.all([
      axios.get(`${API_BASE}/dashboard/summary`).then(r => r.data),
      axios.get(`${API_BASE}/dashboard/kpi`).then(r => r.data).catch(() => null),
    ])
      .then(([s, k]) => { setSummary(s); setKpi(k); })
      .catch(() => toast.error('Failed to load dashboard data'))
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

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

  const kpiBarData = kpi ? {
    labels: ['Processing Time', 'Correction Rate', 'Completeness'],
    datasets: [
      {
        label: 'Achieved (%)',
        data: [
          kpi.processing_time_improvement_pct ?? 0,
          kpi.correction_rate_improvement_pct ?? 0,
          kpi.completeness_rate_pct ?? 0,
        ],
        backgroundColor: '#6366F1',
        borderRadius: 8,
      },
      {
        label: 'Target (%)',
        data: [
          kpi.processing_time_target_pct,
          kpi.correction_rate_target_pct,
          kpi.completeness_target_pct,
        ],
        backgroundColor: 'rgba(99,102,241,0.18)',
        borderRadius: 8,
      },
    ],
  } : null;

  return (
    <div className="app-container">
      <NavBar active="dashboard" />

      <div className="page-content page-fade-in">
        <div className="page-heading">
          <h2>Dashboard</h2>
          <p className="page-sub">System overview at a glance</p>
        </div>

        {/* Top KPI row (operational counters) */}
        <div className="kpi-grid">
          {loading || !summary ? (
            <>
              <KpiSkeleton /><KpiSkeleton /><KpiSkeleton /><KpiSkeleton />
            </>
          ) : (
            <>
              <KpiCard icon="📁" tone="kpi-purple" value={summary.total_cases} label="Total Cases" />
              <KpiCard icon="📄" tone="kpi-blue"   value={summary.total_documents} label="Documents Uploaded" />
              <KpiCard icon="⏳" tone="kpi-yellow" value={summary.pending_review} label="Pending Review" />
              <KpiCard icon="✅" tone="kpi-green"  value={summary.approved} label="Approved" />
            </>
          )}
        </div>

        {/* Sprint 4 — KPI cards (proposal Section 1.3 targets) */}
        <div className="kpi-grid kpi-grid-secondary">
          {loading || !kpi ? (
            <>
              <KpiSkeleton /><KpiSkeleton /><KpiSkeleton /><KpiSkeleton />
            </>
          ) : (
            <>
              <KpiCard
                icon="⏱️" tone="kpi-purple"
                value={kpi.avg_processing_time_minutes !== null
                  ? `${kpi.avg_processing_time_minutes.toFixed(1)} min`
                  : '—'}
                label="Avg Processing Time"
                delta={
                  kpi.processing_time_improvement_pct !== null
                    ? `${kpi.processing_time_improvement_pct.toFixed(1)}% vs baseline · target ≥${kpi.processing_time_target_pct}%`
                    : `Target ≥${kpi.processing_time_target_pct}%`
                }
                onTarget={kpi.processing_time_improvement_pct >= kpi.processing_time_target_pct}
              />
              <KpiCard
                icon="✏️" tone="kpi-yellow"
                value={kpi.correction_rate_per_case !== null
                  ? kpi.correction_rate_per_case.toFixed(2)
                  : '—'}
                label="Corrections / Case"
                delta={
                  kpi.correction_rate_improvement_pct !== null
                    ? `${kpi.correction_rate_improvement_pct.toFixed(1)}% vs baseline · target ≥${kpi.correction_rate_target_pct}%`
                    : `Target ≥${kpi.correction_rate_target_pct}%`
                }
                onTarget={kpi.correction_rate_improvement_pct >= kpi.correction_rate_target_pct}
              />
              <KpiCard
                icon="🎯" tone="kpi-green"
                value={kpi.completeness_rate_pct !== null
                  ? `${kpi.completeness_rate_pct.toFixed(0)}%`
                  : '—'}
                label="Completeness Rate"
                delta={`Target +${kpi.completeness_target_pct}% vs baseline`}
                onTarget={kpi.completeness_rate_pct >= 70 + kpi.completeness_target_pct}
              />
              <KpiCard
                icon="📦" tone="kpi-blue"
                value={kpi.approved_documents}
                label="Approved Documents"
                delta={`Sample size: ${kpi.sample_size}`}
                onTarget
              />
            </>
          )}
        </div>

        {/* KPI bar chart */}
        <div className="card card-fade-in">
          <div className="card-header">
            <h3>KPI Performance vs Target</h3>
            <span className="card-sub">Proposal Section 1.3</span>
          </div>
          {loading || !kpiBarData ? (
            <ChartSkeleton height={280} />
          ) : (
            <div style={{ height: 280 }}>
              <Bar
                data={kpiBarData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { position: 'bottom', labels: { color: cssVar('--text-dark') } } },
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: { callback: v => v + '%', color: cssVar('--text-muted') },
                      title: { display: true, text: '% improvement / completeness', color: cssVar('--text-muted') },
                      grid: { color: cssVar('--border') },
                    },
                    x: {
                      ticks: { color: cssVar('--text-muted') },
                      grid: { color: 'transparent' },
                    },
                  },
                }}
              />
            </div>
          )}
        </div>

        {/* Lower section */}
        <div className="dashboard-lower">
          {/* Recent cases */}
          <div className="card table-card card-fade-in">
            <div className="card-header">
              <h3>Recent Cases</h3>
              <Link to="/cases" className="card-action">View all →</Link>
            </div>
            {loading || !summary ? (
              <TableSkeleton rows={4} cols={5} />
            ) : summary.recent_cases.length === 0 ? (
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
                  {summary.recent_cases.map((c, i) => (
                    <tr key={c.case_id} className="row-fade-in" style={{ animationDelay: `${i * 40}ms` }}>
                      <td><span className="id-pill">#{c.case_id}</span></td>
                      <td>{c.customer}</td>
                      <td>{c.service_type}</td>
                      <td><StatusBadge status={c.status} /></td>
                      <td>
                        <Link to={`/cases/${c.case_id}`} className="table-link">View →</Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Doughnut chart */}
          <div className="card chart-card card-fade-in">
            <div className="card-header">
              <h3>Status Distribution</h3>
            </div>
            {loading || !chartData ? (
              <ChartSkeleton height={280} />
            ) : (
              <div className="chart-wrapper">
                <Doughnut
                  data={chartData}
                  options={{
                    plugins: {
                      legend: {
                        position: 'bottom',
                        labels: { padding: 16, font: { size: 13 }, color: cssVar('--text-dark') },
                      },
                    },
                    cutout: '68%',
                    responsive: true,
                    maintainAspectRatio: true,
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function KpiCard({ icon, tone, value, label, delta, onTarget }) {
  return (
    <div className="kpi-card kpi-card-animated">
      <div className={`kpi-icon ${tone}`}>{icon}</div>
      <div className="kpi-info">
        <span className="kpi-value">{value}</span>
        <span className="kpi-label">{label}</span>
        {delta && (
          <span className={`kpi-delta ${onTarget ? 'kpi-on-target' : 'kpi-below-target'}`}>
            {delta}
          </span>
        )}
      </div>
    </div>
  );
}

function cssVar(name) {
  if (typeof window === 'undefined') return undefined;
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}
