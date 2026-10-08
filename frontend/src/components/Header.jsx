import React from 'react';

export default function Header({ systemHealth }) {
  const isOnline = systemHealth?.status === 'healthy';
  const aiStatus = systemHealth?.ai_status || 'offline';

  return (
    <header className="header">
      <div className="brand-section">
        <div className="brand-icon" role="img" aria-label="Shield">
          🛡️
        </div>
        <div>
          <h1 className="brand-title">API Sentinel</h1>
          <p className="brand-subtitle">AI-Powered API Security & Drift Intelligence</p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <div
          className="status-badge"
          style={{
            background: isOnline ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            borderColor: isOnline ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)',
            color: isOnline ? '#34d399' : '#f87171',
          }}
        >
          <span
            className="status-dot"
            style={{
              background: isOnline ? '#10b981' : '#ef4444',
              boxShadow: isOnline ? '0 0 8px #10b981' : '0 0 8px #ef4444',
            }}
          />
          {isOnline ? 'System Online' : 'System Offline'}
        </div>

        <div
          className="badge"
          style={{
            background: 'rgba(139, 92, 246, 0.15)',
            color: '#c4b5fd',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            padding: '6px 12px',
          }}
        >
          AI: {aiStatus.includes('connected') ? 'Ollama Active' : 'Deterministic Mode'}
        </div>
      </div>
    </header>
  );
}
