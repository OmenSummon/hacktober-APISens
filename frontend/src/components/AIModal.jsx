import React, { useState } from 'react';

export default function AIModal({ finding, aiResult, isLoading, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!finding) return null;

  const handleCopy = () => {
    if (aiResult?.suggested_openapi_patch) {
      navigator.clipboard.writeText(aiResult.suggested_openapi_patch);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="modal-title">AI Security Analysis</span>
              <span className={`risk-badge risk-${finding.severity}`}>
                {finding.severity}
              </span>
            </div>
            <div style={{ fontSize: '0.85rem', color: '#38bdf8', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
              {finding.endpoint}
            </div>
          </div>
          <button type="button" className="modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          {isLoading ? (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <div className="spinner" style={{ width: '28px', height: '28px', marginBottom: '14px' }} />
              <div style={{ color: 'var(--text-muted)' }}>
                Analyzing security posture with AI & deterministic rules...
              </div>
            </div>
          ) : aiResult ? (
            <>
              {/* Provider info pill */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  background: 'rgba(255, 255, 255, 0.03)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.8rem',
                }}
              >
                <span>
                  Engine: <strong style={{ color: '#c4b5fd' }}>{aiResult.provider === 'ollama' ? 'Local Ollama LLM' : 'Deterministic Rule Advisor'}</strong>
                </span>
                <span>
                  Model: <strong style={{ color: '#38bdf8' }}>{aiResult.model}</strong>
                </span>
              </div>

              {/* Technical Explanation */}
              <div className="ai-block">
                <div className="ai-block-title">Technical Root Cause Analysis</div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', whiteSpace: 'pre-line' }}>
                  {aiResult.explanation}
                </div>
              </div>

              {/* Security Impact */}
              <div className="ai-block" style={{ borderLeft: '3px solid #f43f5e' }}>
                <div className="ai-block-title" style={{ color: '#f43f5e' }}>
                  Security & OWASP API Impact
                </div>
                <div style={{ fontSize: '0.88rem', color: 'var(--text-main)' }}>
                  {aiResult.security_impact}
                </div>
              </div>

              {/* Remediation */}
              <div className="ai-block" style={{ borderLeft: '3px solid #10b981' }}>
                <div className="ai-block-title" style={{ color: '#10b981' }}>
                  Recommended Remediation
                </div>
                <div style={{ fontSize: '0.88rem', color: 'var(--text-main)', whiteSpace: 'pre-line' }}>
                  {aiResult.recommended_remediation}
                </div>
              </div>

              {/* Decision on spec addition */}
              <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                Contract Recommendation:{' '}
                <strong style={{ color: aiResult.should_add_to_openapi ? '#34d399' : '#f87171' }}>
                  {aiResult.should_add_to_openapi
                    ? 'Legitimate route — Update OpenAPI specification.'
                    : 'Do NOT document — Decommission or enforce private gateway restrictions.'}
                </strong>
              </div>

              {/* Suggested OpenAPI Patch */}
              {aiResult.suggested_openapi_patch && (
                <div className="ai-block">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div className="ai-block-title">Suggested OpenAPI 3.0 Remediation Patch</div>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                      onClick={handleCopy}
                    >
                      {copied ? '✓ Copied!' : '📋 Copy Patch YAML'}
                    </button>
                  </div>
                  <pre className="code-block">{aiResult.suggested_openapi_patch}</pre>
                </div>
              )}
            </>
          ) : (
            <div style={{ color: '#f87171' }}>Failed to retrieve AI analysis.</div>
          )}
        </div>
      </div>
    </div>
  );
}
