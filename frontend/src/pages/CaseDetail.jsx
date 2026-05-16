import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import { API_BASE } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { NavBar, StatusBadge } from './Dashboard';
import { TableSkeleton } from '../components/Skeleton';

const STATUS_OPTIONS = ['Pending', 'In Review', 'Approved', 'Closed'];

export default function CaseDetail() {
  const { case_id } = useParams();
  const [caseData, setCaseData]   = useState(null);
  const [documents, setDocuments] = useState([]);
  const [audit, setAudit]         = useState([]);          // Sprint 4
  const [activeTab, setActiveTab] = useState('documents'); // Sprint 4: documents | audit
  const [loading, setLoading]     = useState(true);
  const [file, setFile]           = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState('');
  const [uploadErr, setUploadErr] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [exporting, setExporting] = useState('');
  const toast = useToast();

  const fetchData = async () => {
    try {
      const [caseRes, docsRes, auditRes] = await Promise.all([
        axios.get(`${API_BASE}/cases/${case_id}`),
        axios.get(`${API_BASE}/cases/${case_id}/documents/`),
        axios.get(`${API_BASE}/cases/${case_id}/audit`).catch(() => ({ data: [] })),
      ]);
      setCaseData(caseRes.data);
      setDocuments(docsRes.data);
      setAudit(auditRes.data || []);
    } catch {
      setCaseData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [case_id]);

  // Sprint 4 — Export to Excel / PDF
  const handleExport = async (kind) => {
    setExporting(kind);
    try {
      const res = await axios.get(
        `${API_BASE}/cases/${case_id}/export/${kind}`,
        { responseType: 'blob' },
      );
      const ext = kind === 'excel' ? 'xlsx' : 'pdf';
      const blob = new Blob([res.data]);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `case_${case_id}_export.${ext}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`${ext.toUpperCase()} export downloaded`);
    } catch {
      toast.error(`Failed to export ${kind.toUpperCase()}`);
    } finally {
      setExporting('');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return setUploadErr('Please select a PDF file first');
    if (file.type !== 'application/pdf') return setUploadErr('Only PDF files are accepted');

    setUploading(true);
    setUploadMsg('');
    setUploadErr('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API_BASE}/cases/${case_id}/documents/`, formData);
      setUploadMsg(`"${res.data.filename}" uploaded successfully.`);
      setFile(null);
      e.target.reset();
      toast.success(`Uploaded ${res.data.filename}`);
      fetchData();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Upload failed';
      setUploadErr(msg);
      toast.error(msg);
    } finally {
      setUploading(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    setUpdatingStatus(true);
    try {
      await axios.put(`${API_BASE}/cases/${case_id}?new_status=${encodeURIComponent(newStatus)}`);
      setCaseData(prev => ({ ...prev, status: newStatus }));
      toast.success(`Status updated to "${newStatus}"`);
    } catch {
      toast.error('Failed to update status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  if (loading) return (
    <div className="app-container">
      <NavBar active="cases" />
      <div className="page-content page-fade-in">
        <TableSkeleton rows={5} cols={4} />
      </div>
    </div>
  );

  if (!caseData) return (
    <div className="app-container">
      <NavBar active="cases" />
      <div className="page-content">
        <div className="empty-state">
          Case not found. <Link to="/cases">Back to cases</Link>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app-container">
      <NavBar active="cases" />

      <div className="page-content page-fade-in">
        {/* Breadcrumb */}
        <div className="breadcrumb">
          <Link to="/cases">Cases</Link>
          <span className="breadcrumb-sep">/</span>
          <span>Case #{case_id}</span>
        </div>

        {/* Case summary card */}
        <div className="card case-header-card card-fade-in">
          <div className="case-meta-grid">
            <div className="meta-item">
              <span className="meta-label">Customer</span>
              <span className="meta-value fw-medium">{caseData.customer}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Service Type</span>
              <span className="meta-value">{caseData.service_type}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Created</span>
              <span className="meta-value">
                {caseData.created_at ? new Date(caseData.created_at).toLocaleDateString() : '—'}
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Status</span>
              <div className="status-control">
                <StatusBadge status={caseData.status} />
                <select
                  className="status-select"
                  value={caseData.status}
                  onChange={e => handleStatusChange(e.target.value)}
                  disabled={updatingStatus}
                >
                  {STATUS_OPTIONS.map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Upload section */}
        <div className="card">
          <h3 className="card-title">Upload Document</h3>
          <form onSubmit={handleUpload} className="upload-row">
            <input
              type="file"
              accept="application/pdf"
              onChange={e => { setFile(e.target.files[0]); setUploadErr(''); setUploadMsg(''); }}
            />
            <button type="submit" className="btn-primary" disabled={uploading}>
              {uploading ? 'Uploading…' : 'Upload PDF'}
            </button>
          </form>
          {uploadMsg && <p className="msg-success">{uploadMsg}</p>}
          {uploadErr && <p className="msg-error">{uploadErr}</p>}
        </div>

        {/* Sprint 4 — Export buttons (US4) */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Export Case</h3>
            <span className="card-sub">Generate a standard output deliverable</span>
          </div>
          <div className="export-row">
            <button
              className="btn-secondary"
              onClick={() => handleExport('excel')}
              disabled={!!exporting}
            >
              {exporting === 'excel' ? 'Generating…' : '📊 Export to Excel'}
            </button>
            <button
              className="btn-secondary"
              onClick={() => handleExport('pdf')}
              disabled={!!exporting}
            >
              {exporting === 'pdf' ? 'Generating…' : '📄 Export to PDF'}
            </button>
          </div>
        </div>

        {/* Sprint 4 — Tabbed pane: Documents | Audit Trail */}
        <div className="card">
          <div className="tab-bar">
            <button
              className={`tab-btn ${activeTab === 'documents' ? 'active' : ''}`}
              onClick={() => setActiveTab('documents')}
            >
              Documents <span className="count-pill">{documents.length}</span>
            </button>
            <button
              className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
              onClick={() => setActiveTab('audit')}
            >
              Audit Trail <span className="count-pill">{audit.length}</span>
            </button>
          </div>

          {activeTab === 'documents' && (
            documents.length === 0 ? (
              <div className="empty-state">No documents uploaded yet.</div>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Doc ID</th>
                    <th>Filename</th>
                    <th>Uploaded</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map(doc => (
                    <tr key={doc.doc_id}>
                      <td><span className="id-pill">#{doc.doc_id}</span></td>
                      <td className="fw-medium">{doc.file_path.split('/').pop()}</td>
                      <td className="text-muted">
                        {doc.upload_time ? new Date(doc.upload_time).toLocaleString() : '—'}
                      </td>
                      <td>
                        <Link
                          to={`/cases/${case_id}/documents/${doc.doc_id}/review`}
                          className="btn-sm btn-view"
                        >
                          Review →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          )}

          {activeTab === 'audit' && (
            audit.length === 0 ? (
              <div className="empty-state">No changes recorded yet for this case.</div>
            ) : (
              <table className="data-table audit-table">
                <thead>
                  <tr>
                    <th>When</th>
                    <th>Doc</th>
                    <th>Field</th>
                    <th>Old Value</th>
                    <th>New Value</th>
                    <th>User</th>
                  </tr>
                </thead>
                <tbody>
                  {audit.map(a => (
                    <tr key={a.change_id}>
                      <td className="text-muted">
                        {a.changed_at ? new Date(a.changed_at).toLocaleString() : '—'}
                      </td>
                      <td><span className="id-pill">#{a.doc_id}</span></td>
                      <td className="fw-medium">{a.field_name}</td>
                      <td className="audit-old">{a.old_value || '—'}</td>
                      <td className="audit-new">{a.new_value || '—'}</td>
                      <td className="text-muted">#{a.changed_by}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          )}
        </div>
      </div>
    </div>
  );
}
