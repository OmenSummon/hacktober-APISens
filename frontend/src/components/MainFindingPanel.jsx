import React, { useState } from 'react';

export default function MainFindingPanel({ findings, onSelectAI }) {
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [filterType, setFilterType] = useState('ALL');

  const filtered = (findings || []).filter((f) => {
    if (filterSeverity !== 'ALL' && f.severity !== filterSeverity) return false;
    if (filterType !== 'ALL' && f.type !== filterType) return false;
    return true;
  });

  const getSeverityColor = (sev) => {
    switch (sev) {
      case 'CRITICAL': return '#f43f5e';
      case 'HIGH': return '#ef4444';
      case 'MEDIUM': return '#f59e0b';
      case 'LOW': return '#3b82f6';
      default: return '#10b981';
    }
  };

  return (
    <div className="section-card">
      <div className="section-header">
        <div className="section-title">
          <span>🚨</span>
          <span>Security Discrepancies & Findings</span>
          <span
            style={{
              fontSize: '0.82rem',
              color: 'var(--text-dim)',
              background: 'rgba(255, 255, 255, 0.06)',
              padding: '2px 8px',
              borderRadius: '999px',
            }}
          >
            {filtered.length} of {findings?.length || 0}
          </span>
        </div>

        {/* Filter controls */}
        <div style={{ display: 'flex', gap: '10px' }}>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            style={{
              background: 'var(--bg-elevated)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-subtle)',
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
            }}
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            style={{
              background: 'var(--bg-elevated)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-subtle)',
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
            }}
          >
            <option value="ALL">All Finding Types</option>
            <option value="SHADOW_ENDPOINT">Shadow Endpoint</option>
            <option value="SCHEMA_DRIFT">Schema Drift</option>
            <option value="PARAMETER_DRIFT">Parameter Drift</option>
            <option value="UNDOCUMENTED_METHOD">Undocumented Method</option>
            <option value="AUTH_MISMATCH">Auth Mismatch</option>
          </select>
        </div>
      </div>

      <div className="findings-list">
        {filtered.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No security findings matching current filters. Run a scan or load demo data to view detections.
          </div>
        ) : (
          filtered.map((item) => (
            <div
              key={item.id}
              className="finding-card"
              style={{ '--finding-color': getSeverityColor(item.severity) }}
            >
              <div className="finding-top">
                <div className="finding-badges">
                  {item.is_latest && (
                    <span className="badge-latest">✨ LATEST</span>
                  )}
                  <span className={`risk-badge risk-${item.severity}`}>
                    {item.severity}
                  </span>
                  <span className="badge badge-type">{item.type.replace('_', ' ')}</span>
                  <span className="badge badge-method">{item.method}</span>
                  <span className="endpoint-tag">{item.path}</span>
                </div>


                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                    Risk: <strong style={{ color: getSeverityColor(item.severity) }}>{item.risk_score}/100</strong>
                  </span>
                  <button
                    type="button"
                    className="btn btn-ai"
                    onClick={() => onSelectAI(item)}
                    id={`ai-btn-${item.id}`}
                  >
                    ✨ AI Analysis & Patch
                  </button>
                </div>
              </div>

              <div className="finding-title">{item.title}</div>
              <div className="finding-desc">{item.description}</div>

              <div className="finding-footer">
                <div className="finding-meta">
                  <span>Observed Traffic: <strong>{item.observed_count} reqs</strong></span>
                  {item.details?.owasp_category && (
                    <span>OWASP: <strong style={{ color: '#c4b5fd' }}>{item.details.owasp_category}</strong></span>
                  )}
                  {item.details?.is_authenticated !== undefined && (
                    <span>
                      Auth:{' '}
                      <strong style={{ color: item.details.is_authenticated ? '#34d399' : '#f87171' }}>
                        {item.details.is_authenticated ? 'Verified' : 'Unauthenticated'}
                      </strong>
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
