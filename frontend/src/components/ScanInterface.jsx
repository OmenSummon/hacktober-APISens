import React, { useRef } from 'react';

export default function ScanInterface({
  specFile,
  trafficFile,
  isDemo,
  scanSummary,
  onSetSpecFile,
  onSetTrafficFile,
  onRunDemo,
  onRunFiles,
  onClear,
  isLoading,
  error,
  notification,
}) {
  const specInputRef = useRef(null);
  const trafficInputRef = useRef(null);

  const handleCustomScan = (e) => {
    e.preventDefault();
    if (!specFile || !trafficFile) {
      alert('Please upload or load both an OpenAPI specification file and a traffic JSON file.');
      return;
    }
    onRunFiles(specFile, trafficFile);
  };

  const handleDownload = (file) => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleClearAll = () => {
    if (specInputRef.current) specInputRef.current.value = '';
    if (trafficInputRef.current) trafficInputRef.current.value = '';
    onClear();
  };

  return (
    <div className="scan-bar">
      <div className="scan-bar-header">
        <div className="scan-title">
          <span>🔍</span>
          <span>Security Scan & Ingestion Engine</span>
        </div>
        <div className="scan-actions">
          <button
            type="button"
            className="btn btn-demo"
            onClick={onRunDemo}
            disabled={isLoading}
            id="load-demo-btn"
          >
            {isLoading ? <span className="spinner" /> : '⚡ Load Demo Data'}
          </button>

          <button
            type="button"
            className="btn btn-primary"
            onClick={handleCustomScan}
            disabled={isLoading || !specFile || !trafficFile}
            id="run-scan-btn"
          >
            {isLoading ? <span className="spinner" /> : '🛡️ Run Security Scan'}
          </button>

          {(specFile || trafficFile) && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleClearAll}
              disabled={isLoading}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="inputs-grid">
        {/* OpenAPI Specification Box */}
        <div className={`input-box ${specFile ? (isDemo ? 'demo-active' : 'active-file') : ''}`}>
          <div className="input-label">
            <span>1. OpenAPI 3.x Specification</span>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>.yaml, .yml, .json</span>
          </div>

          {specFile && (
            <div className="file-status-row">
              <div className="file-status-left">
                <span style={{ color: '#38bdf8' }}>📄</span>
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{specFile.name}</span>
                <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                  ({(specFile.size / 1024).toFixed(1)} KB)
                </span>
                {isDemo && <span className="badge-demo">Demo</span>}
              </div>
              <button
                type="button"
                className="btn-xs"
                onClick={() => handleDownload(specFile)}
                title="Download or view this file"
              >
                ⬇️ View / Save
              </button>
            </div>
          )}

          <input
            ref={specInputRef}
            type="file"
            accept=".yaml,.yml,.json"
            className="file-input"
            onChange={(e) => onSetSpecFile(e.target.files[0] || null)}
            id="openapi-file-input"
          />
        </div>

        {/* Traffic Batch Box */}
        <div className={`input-box ${trafficFile ? (isDemo ? 'demo-active' : 'active-file') : ''}`}>
          <div className="input-label">
            <span>2. Observed API Traffic</span>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>JSON Batch</span>
          </div>

          {trafficFile && (
            <div className="file-status-row">
              <div className="file-status-left">
                <span style={{ color: '#a78bfa' }}>🌐</span>
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{trafficFile.name}</span>
                <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                  ({(trafficFile.size / 1024).toFixed(1)} KB)
                </span>
                {isDemo && <span className="badge-demo">Demo</span>}
              </div>
              <button
                type="button"
                className="btn-xs"
                onClick={() => handleDownload(trafficFile)}
                title="Download or view this file"
              >
                ⬇️ View / Save
              </button>
            </div>
          )}

          <input
            ref={trafficInputRef}
            type="file"
            accept=".json"
            className="file-input"
            onChange={(e) => onSetTrafficFile(e.target.files[0] || null)}
            id="traffic-file-input"
          />
        </div>
      </div>

      {notification && (
        <div className="notification-banner">
          <span>{notification}</span>
        </div>
      )}

      {scanSummary && (
        <div className="scan-summary-pill">
          <div>
            <strong style={{ color: '#c4b5fd' }}>⚡ Active Scan Results:</strong>{' '}
            <span>{scanSummary.total_observed_endpoints || 0} observed endpoints</span> •{' '}
            <span style={{ color: '#fca5a5', fontWeight: 600 }}>
              {scanSummary.shadow_endpoints || 0} shadow endpoints
            </span>{' '}
            •{' '}
            <span style={{ color: '#fde68a' }}>
              {(scanSummary.schema_drifts || 0) + (scanSummary.parameter_drifts || 0)} drifts
            </span>{' '}
            •{' '}
            <span>
              Risk Level:{' '}
              <span className={`risk-badge risk-${scanSummary.risk_level || 'CLEAN'}`}>
                {scanSummary.risk_level} ({scanSummary.risk_score}/100)
              </span>
            </span>
          </div>
          <button
            type="button"
            className="btn-xs"
            onClick={() => {
              const el = document.getElementById('scan-results-section');
              if (el) el.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            View Details ↓
          </button>
        </div>
      )}

      {error && (
        <div
          style={{
            marginTop: '14px',
            padding: '10px 16px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-sm)',
            color: '#fca5a5',
            fontSize: '0.85rem',
          }}
        >
          ⚠️ Error: {error}
        </div>
      )}
    </div>
  );
}
