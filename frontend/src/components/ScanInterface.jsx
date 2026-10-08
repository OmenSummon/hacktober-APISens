import React, { useRef, useState } from 'react';

export default function ScanInterface({ onRunDemo, onRunFiles, isLoading, error }) {
  const [specFile, setSpecFile] = useState(null);
  const [trafficFile, setTrafficFile] = useState(null);

  const specInputRef = useRef(null);
  const trafficInputRef = useRef(null);

  const handleCustomScan = (e) => {
    e.preventDefault();
    if (!specFile || !trafficFile) {
      alert('Please upload both an OpenAPI specification file and a traffic JSON file.');
      return;
    }
    onRunFiles(specFile, trafficFile);
  };

  const handleClear = () => {
    setSpecFile(null);
    setTrafficFile(null);
    if (specInputRef.current) specInputRef.current.value = '';
    if (trafficInputRef.current) trafficInputRef.current.value = '';
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
            disabled={isLoading || (!specFile && !trafficFile)}
            id="run-scan-btn"
          >
            {isLoading ? <span className="spinner" /> : '🛡️ Run Security Scan'}
          </button>

          {(specFile || trafficFile) && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleClear}
              disabled={isLoading}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="inputs-grid">
        <div className={`input-box ${specFile ? 'active-file' : ''}`}>
          <div className="input-label">
            <span>1. OpenAPI 3.x Specification</span>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>.yaml, .yml, .json</span>
          </div>
          <input
            ref={specInputRef}
            type="file"
            accept=".yaml,.yml,.json"
            className="file-input"
            onChange={(e) => setSpecFile(e.target.files[0] || null)}
            id="openapi-file-input"
          />
          {specFile && (
            <span style={{ fontSize: '0.8rem', color: '#38bdf8' }}>
              ✓ Selected: {specFile.name} ({(specFile.size / 1024).toFixed(1)} KB)
            </span>
          )}
        </div>

        <div className={`input-box ${trafficFile ? 'active-file' : ''}`}>
          <div className="input-label">
            <span>2. Observed API Traffic</span>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>JSON Batch</span>
          </div>
          <input
            ref={trafficInputRef}
            type="file"
            accept=".json"
            className="file-input"
            onChange={(e) => setTrafficFile(e.target.files[0] || null)}
            id="traffic-file-input"
          />
          {trafficFile && (
            <span style={{ fontSize: '0.8rem', color: '#38bdf8' }}>
              ✓ Selected: {trafficFile.name} ({(trafficFile.size / 1024).toFixed(1)} KB)
            </span>
          )}
        </div>
      </div>

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
