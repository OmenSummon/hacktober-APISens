import React from 'react';

export default function SummaryCards({ summary }) {
  const s = summary || {
    total_documented_endpoints: 0,
    total_observed_endpoints: 0,
    shadow_endpoints: 0,
    schema_drifts: 0,
    parameter_drifts: 0,
    risk_score: 0,
    risk_level: 'CLEAN',
  };

  const totalDrifts = (s.schema_drifts || 0) + (s.parameter_drifts || 0);

  return (
    <div className="summary-grid">
      <div className="summary-card" style={{ '--card-accent': '#10b981' }}>
        <div className="summary-label">Documented Endpoints</div>
        <div className="summary-value" style={{ color: '#6ee7b7' }}>
          {s.total_documented_endpoints}
        </div>
        <div className="summary-subtext">OpenAPI 3.x defined contracts</div>
      </div>

      <div className="summary-card" style={{ '--card-accent': '#3b82f6' }}>
        <div className="summary-label">Observed Endpoints</div>
        <div className="summary-value" style={{ color: '#93c5fd' }}>
          {s.total_observed_endpoints}
        </div>
        <div className="summary-subtext">Discovered from real traffic</div>
      </div>

      <div className="summary-card" style={{ '--card-accent': '#ef4444' }}>
        <div className="summary-label">Shadow Endpoints</div>
        <div className="summary-value" style={{ color: '#fca5a5' }}>
          {s.shadow_endpoints}
        </div>
        <div className="summary-subtext">Undocumented live routes (OWASP API9)</div>
      </div>

      <div className="summary-card" style={{ '--card-accent': '#f59e0b' }}>
        <div className="summary-label">Schema & Param Drifts</div>
        <div className="summary-value" style={{ color: '#fde68a' }}>
          {totalDrifts}
        </div>
        <div className="summary-subtext">
          {s.schema_drifts || 0} body, {s.parameter_drifts || 0} query params
        </div>
      </div>

      <div className="summary-card" style={{ '--card-accent': '#8b5cf6' }}>
        <div className="summary-label">Overall Risk Score</div>
        <div style={{ display: 'flex', alignItems: 'baseline' }}>
          <span className="summary-value">{s.risk_score}</span>
          <span style={{ fontSize: '1rem', color: 'var(--text-dim)', marginLeft: '4px' }}>
            /100
          </span>
          <span className={`risk-badge risk-${s.risk_level || 'CLEAN'}`}>
            {s.risk_level || 'CLEAN'}
          </span>
        </div>
        <div className="summary-subtext">Deterministic OWASP evaluation</div>
      </div>
    </div>
  );
}
