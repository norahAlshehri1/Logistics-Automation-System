import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import { API_BASE } from '../context/AuthContext';
import { NavBar } from './Dashboard';

const FIELDS = ['Vendor Name', 'Invoice Number', 'Shipment Date', 'Total Amount'];

const CONFIDENCE_STYLE = {
  High:   { background: '#D1FAE5', color: '#065F46' },
  Medium: { background: '#FEF3C7', color: '#92400E' },
  Low:    { background: '#FEE2E2', color: '#991B1B' },
};

export default function ReviewPage() {
  const { case_id, doc_id } = useParams();

  const [data, setData] = useState(
    Object.fromEntries(FIELDS.map(f => [f, '']))
  );
  const [confidence, setConfidence] = useState(null);
  const [language, setLanguage]     = useState(null);
  const [status, setStatus]         = useState('Click "Extract Data" to begin.');
  const [statusType, setStatusType] = useState('idle'); // idle | loading | success | error
  const [extracted, setExtracted]   = useState(false);
  const [approved, setApproved]     = useState(false);
  const [pdfUrl, setPdfUrl]         = useState(null);

  // Load previously extracted data on mount
  useEffect(() => {
    axios.get(`${API_BASE}/documents/${doc_id}/fields`)
      .then(res => {
        if (res.data.length > 0) {
          const merged = { ...data };
          res.data.forEach(f => {
            if (FIELDS.includes(f.field_name)) {
              merged[f.field_name] = f.approved_value ?? f.extracted_value ?? '';
              if (f.approved_value) setApproved(true);
            }
          });
          setData(merged);
          setExtracted(true);
          setStatus('Previously extracted data loaded. Review and approve.');
          setStatusType('success');
        }
      })
      .catch(() => {});
  }, [doc_id]);

  const setMsg = (msg, type = 'idle') => { setStatus(msg); setStatusType(type); };

  const handleExtract = async () => {
    setMsg('Extracting data from document…', 'loading');
    setApproved(false);
    try {
      const res = await axios.post(`${API_BASE}/documents/${doc_id}/extract`);
      const raw = res.data.extracted_data || {};
      const merged = Object.fromEntries(FIELDS.map(f => [f, raw[f] ?? '']));
      setData(merged);
      setConfidence(res.data.confidence_score);
      setLanguage(res.data.language);
      setExtracted(true);
      setMsg(
        `Extracted successfully — Confidence: ${res.data.confidence_score} | Language: ${res.data.language}`,
        'success'
      );
    } catch (err) {
      setMsg('Extraction failed: ' + (err.response?.data?.detail || err.message), 'error');
    }
  };

  const handleApprove = async () => {
    setMsg('Saving approved data…', 'loading');
    try {
      await axios.put(`${API_BASE}/documents/${doc_id}/approve`, data);
      setApproved(true);
      setMsg('Data approved and saved successfully!', 'success');
    } catch (err) {
      setMsg('Approval failed: ' + (err.response?.data?.detail || err.message), 'error');
    }
  };

  const statusClass = {
    idle:    'status-idle',
    loading: 'status-loading',
    success: 'status-success',
    error:   'status-error',
  }[statusType];

  return (
    <div className="app-container">
      <NavBar active="cases" />

      {/* Status bar */}
      <div className={`review-status-bar ${statusClass}`}>
        <span className="status-text">
          {statusType === 'loading' && <span className="status-spinner" />}
          {status}
        </span>
        <div className="status-badges">
          {confidence && (
            <span className="conf-badge" style={CONFIDENCE_STYLE[confidence] || {}}>
              Confidence: {confidence}
            </span>
          )}
          {language && (
            <span className="lang-badge">
              {language === 'arabic' ? '🇸🇦 Arabic' : '🇬🇧 English'}
            </span>
          )}
        </div>
      </div>

      {/* Breadcrumb */}
      <div className="review-breadcrumb">
        <Link to="/cases">Cases</Link>
        <span> / </span>
        <Link to={`/cases/${case_id}`}>Case #{case_id}</Link>
        <span> / </span>
        <span>Document #{doc_id} Review</span>
      </div>

      <div className="main-content">
        {/* Left: Document viewer */}
        <div className="left-pane">
          <div className="pane-header">
            <h2>1. Document</h2>
            <button
              className="btn-primary btn-sm-text"
              onClick={handleExtract}
              disabled={statusType === 'loading'}
            >
              {extracted ? '🔄 Re-Extract' : '⚡ Extract Data'}
            </button>
          </div>

          <div className="pdf-placeholder">
            <div className="pdf-placeholder-icon">📄</div>
            <p className="pdf-placeholder-title">Document #{doc_id}</p>
            <p className="pdf-placeholder-sub">
              Click <strong>Extract Data</strong> to run the extraction pipeline on this document.
            </p>
            <p className="pdf-placeholder-sub">
              The system will detect if the PDF is digital or scanned, and whether it&apos;s in English or Arabic.
            </p>
          </div>
        </div>

        {/* Right: Review form */}
        <div className="right-pane">
          <h2>2. Review &amp; Edit Data</h2>
          <div className="form-container">
            {FIELDS.map(key => (
              <div className="form-group" key={key}>
                <label>{key}</label>
                <input
                  type="text"
                  name={key}
                  value={data[key] || ''}
                  onChange={e => setData(prev => ({ ...prev, [key]: e.target.value }))}
                  disabled={approved}
                  placeholder={extracted ? '(not detected)' : 'Run extraction first'}
                />
              </div>
            ))}

            {approved ? (
              <div className="approved-banner">
                ✅ Data approved and saved
              </div>
            ) : (
              <button
                className="approve-btn"
                onClick={handleApprove}
                disabled={!extracted || statusType === 'loading'}
              >
                Approve &amp; Save Final Data
              </button>
            )}

            <Link to={`/cases/${case_id}`} className="btn-back">
              ← Back to Case #{case_id}
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
