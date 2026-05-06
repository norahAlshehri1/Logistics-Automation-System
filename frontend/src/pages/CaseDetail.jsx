import { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE } from '../context/AuthContext';
import { NavBar, StatusBadge } from './Dashboard';

const STATUS_OPTIONS = ['Pending', 'In Review', 'Approved', 'Closed'];

export default function CaseDetail() {
  const { case_id } = useParams();
  const [caseData, setCaseData]   = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [file, setFile]           = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState('');
  const [uploadErr, setUploadErr] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      const [caseRes, docsRes] = await Promise.all([
        axios.get(`${API_BASE}/cases/${case_id}`),
        axios.get(`${API_BASE}/cases/${case_id}/documents/`),
      ]);
      setCaseData(caseRes.data);
      setDocuments(docsRes.data);
    } catch {
      setCaseData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [case_id]);

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
      fetchData();
    } catch (err) {
      setUploadErr(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    setUpdatingStatus(true);
    try {
      await axios.put(`${API_BASE}/cases/${case_id}?new_status=${newStatus}`);
      setCaseData(prev => ({ ...prev, status: newStatus }));
    } catch {
      alert('Failed to update status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  if (loading) return (
    <div className="app-container">
      <NavBar active="cases" />
      <div className="loading-state">Loading case…</div>
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

      <div className="page-content">
        {/* Breadcrumb */}
        <div className="breadcrumb">
          <Link to="/cases">Cases</Link>
          <span className="breadcrumb-sep">/</span>
          <span>Case #{case_id}</span>
        </div>

        {/* Case summary card */}
        <div className="card case-header-card">
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

        {/* Documents table */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Documents <span className="count-pill">{documents.length}</span></h3>
          </div>
          {documents.length === 0 ? (
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
          )}
        </div>
      </div>
    </div>
  );
}
