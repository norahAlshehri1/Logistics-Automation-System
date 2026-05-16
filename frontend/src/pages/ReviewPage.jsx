import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import { API_BASE } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { NavBar } from './Dashboard';

const FIELDS = ['Vendor Name', 'Invoice Number', 'Shipment Date', 'Total Amount'];

const CONFIDENCE_STYLE = {
  High:    { background: '#D1FAE5', color: '#065F46' },
  Medium:  { background: '#FEF3C7', color: '#92400E' },
  Low:     { background: '#FEE2E2', color: '#991B1B' },
  Missing: { background: '#F3F4F6', color: '#374151' },
};

const FIELD_CONFIDENCE_TONE = {
  High:    'conf-high',
  Medium:  'conf-medium',
  Low:     'conf-low',
  Missing: 'conf-missing',
};

export default function ReviewPage() {
  const { case_id, doc_id } = useParams();
  const toast = useToast();

  const [data, setData] = useState(
    Object.fromEntries(FIELDS.map(f => [f, '']))
  );
  const [fieldConfidence, setFieldConfidence] = useState({});  // Sprint 4: per-field
  const [confidence, setConfidence] = useState(null);          // overall
  const [language, setLanguage]     = useState(null);
  const [status, setStatus]         = useState('Click "Extract Data" to begin.');
  const [statusType, setStatusType] = useState('idle'); // idle | loading | success | error
  const [extracted, setExtracted]   = useState(false);
  const [approved, setApproved]     = useState(false);
  const [pdfUrl, setPdfUrl]         = useState(null);
  const [pdfErr, setPdfErr]         = useState(false);

  // ── Load PDF + previously extracted data on mount ──────────────────────────
  useEffect(() => {
    let revokeUrl = null;

    // Sprint 4 — fetch PDF as blob (auth header already on axios defaults).
    axios.get(`${API_BASE}/documents/${doc_id}/file`, { responseType: 'blob' })
      .then(res => {
        const blob = new Blob([res.data], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        revokeUrl = url;
        setPdfUrl(url);
      })
      .catch(() => setPdfErr(true));

    axios.get(`${API_BASE}/documents/${doc_id}/fields`)
      .then(res => {
        if (res.data.length > 0) {
          const merged = Object.fromEntries(FIELDS.map(f => [f, '']));
          const confMap = {};
          res.data.forEach(f => {
            if (FIELDS.includes(f.field_name)) {
              merged[f.field_name] = f.approved_value ?? f.extracted_value ?? '';
              confMap[f.field_name] = f.confidence || 'Medium';
              if (f.approved_value) setApproved(true);
            }
          });
          setData(merged);
          setFieldConfidence(confMap);
          setExtracted(true);
          setStatus('Previously extracted data loaded. Review and approve.');
          setStatusType('success');
        }
      })
      .catch(() => {});

    return () => { if (revokeUrl) URL.revokeObjectURL(revokeUrl); };
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
      setFieldConfidence(res.data.field_confidence || {});
      setExtracted(true);
      const lowFields = Object.entries(res.data.field_confidence || {})
        .filter(([, v]) => v === 'Low' || v === 'Missing')
        .map(([k]) => k);
      const msg = `Extracted · Overall: ${res.data.confidence_score} · ${res.data.language === 'arabic' ? 'Arabic' : 'English'}`;
      setMsg(msg, 'success');
      if (lowFields.length > 0) {
        toast.warning(`Review needed for: ${lowFields.join(', ')}`);
      } else {
        toast.success('Extraction completed cleanly');
      }
    } catch (err) {
      const m = 'Extraction failed: ' + (err.response?.data?.detail || err.message);
      setMsg(m, 'error');
      toast.error(m);
    }
  };

  const handleApprove = async () => {
    setMsg('Saving approved data…', 'loading');
    try {
      await axios.put(`${API_BASE}/documents/${doc_id}/approve`, data);
      setApproved(true);
      setMsg('Data approved and saved successfully!', 'success');
      toast.success('Approved & saved');
    } catch (err) {
      const m = 'Approval failed: ' + (err.response?.data?.detail || err.message);
      setMsg(m, 'error');
      toast.error(m);
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

      <div className="main-content review-grid">
        {/* Left: real PDF viewer */}
        <div className="left-pane review-pane">
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

          {pdfUrl ? (
            <iframe
              src={pdfUrl}
              title={`Document #${doc_id}`}
              className="pdf-frame"
            />
          ) : pdfErr ? (
            <div className="pdf-placeholder">
              <div className="pdf-placeholder-icon">⚠️</div>
              <p className="pdf-placeholder-title">Document #{doc_id}</p>
              <p className="pdf-placeholder-sub">
                The PDF couldn't be loaded. The file may be missing on disk.
              </p>
            </div>
          ) : (
            <div className="pdf-placeholder">
              <div className="pdf-loading-pulse" />
              <p className="pdf-placeholder-title">Loading document…</p>
            </div>
          )}
        </div>

        {/* Right: review form with per-field confidence */}
        <div className="right-pane review-pane">
          <h2>2. Review &amp; Edit Data</h2>
          <div className="form-container">
            {FIELDS.map(key => {
              const conf = fieldConfidence[key];
              const tone = FIELD_CONFIDENCE_TONE[conf] || '';
              return (
                <div className={`form-group form-group-confident ${tone}`} key={key}>
                  <div className="form-label-row">
                    <label>{key}</label>
                    {conf && (
                      <span className="conf-pill" style={CONFIDENCE_STYLE[conf] || {}}>
                        {conf}
                      </span>
                    )}
                  </div>
                  <input
                    type="text"
                    name={key}
                    value={data[key] || ''}
                    onChange={e => setData(prev => ({ ...prev, [key]: e.target.value }))}
                    disabled={approved}
                    placeholder={extracted ? '(not detected — please fill in)' : 'Run extraction first'}
                  />
                </div>
              );
            })}

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
