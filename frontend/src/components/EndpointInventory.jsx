import React, { useState } from 'react';

export default function EndpointInventory({ inventory }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filtered = (inventory || []).filter((item) => {
    if (statusFilter !== 'ALL' && item.status !== statusFilter) return false;
    if (searchTerm) {
      const matchPath = item.endpoint.toLowerCase().includes(searchTerm.toLowerCase());
      const matchMethod = item.method.toLowerCase().includes(searchTerm.toLowerCase());
      return matchPath || matchMethod;
    }
    return true;
  });

  return (
    <div className="section-card">
      <div className="section-header">
        <div className="section-title">
          <span>📋</span>
          <span>Endpoint Inventory & Observability Matrix</span>
          <span
            style={{
              fontSize: '0.82rem',
              color: 'var(--text-dim)',
              background: 'rgba(255, 255, 255, 0.06)',
              padding: '2px 8px',
              borderRadius: '999px',
            }}
          >
            {filtered.length} endpoints
          </span>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            placeholder="Search path or method..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              background: 'var(--bg-elevated)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-subtle)',
              padding: '6px 12px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              width: '200px',
            }}
          />

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              background: 'var(--bg-elevated)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-subtle)',
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
            }}
          >
            <option value="ALL">All Statuses</option>
            <option value="HEALTHY">Healthy</option>
            <option value="SHADOW">Shadow</option>
            <option value="DRIFT">Drift</option>
            <option value="UNOBSERVED">Unobserved</option>
          </select>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="inventory-table">
          <thead>
            <tr>
              <th>Method</th>
              <th>Endpoint Path</th>
              <th style={{ textAlign: 'center' }}>Documented</th>
              <th style={{ textAlign: 'center' }}>Observed</th>
              <th>Status</th>
              <th>Risk Level</th>
              <th style={{ textAlign: 'right' }}>Requests</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-dim)' }}>
                  No endpoints matching current search/filters.
                </td>
              </tr>
            ) : (
              filtered.map((item, idx) => (
                <tr key={`${item.method}-${item.endpoint}-${idx}`}>
                  <td className="cell-method" style={{ color: item.method === 'GET' ? '#38bdf8' : item.method === 'POST' ? '#34d399' : '#f59e0b' }}>
                    {item.method}
                  </td>
                  <td className="cell-endpoint">{item.endpoint}</td>
                  <td style={{ textAlign: 'center' }}>
                    {item.documented ? (
                      <span style={{ color: '#34d399', fontWeight: 'bold' }}>YES</span>
                    ) : (
                      <span style={{ color: '#f87171', fontWeight: 'bold' }}>NO</span>
                    )}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    {item.observed ? (
                      <span style={{ color: '#38bdf8', fontWeight: 'bold' }}>YES</span>
                    ) : (
                      <span style={{ color: 'var(--text-dim)' }}>NO</span>
                    )}
                  </td>
                  <td>
                    <span className={`status-tag status-${item.status}`}>
                      {item.status}
                    </span>
                  </td>
                  <td>
                    <span className={`risk-badge risk-${item.risk}`}>
                      {item.risk}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right', fontFamily: 'var(--font-mono)' }}>
                    {item.request_count}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
