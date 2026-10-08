import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import SummaryCards from '../components/SummaryCards';
import ScanInterface from '../components/ScanInterface';
import MainFindingPanel from '../components/MainFindingPanel';
import EndpointInventory from '../components/EndpointInventory';
import AIModal from '../components/AIModal';
import {
  analyzeFindingWithAI,
  fetchBaselineScan,
  fetchDemoFiles,
  fetchHealth,
  runDemoScan,
  runScanWithFiles,
} from '../services/api';

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [scanError, setScanError] = useState(null);

  // Active files state
  const [specFile, setSpecFile] = useState(null);
  const [trafficFile, setTrafficFile] = useState(null);
  const [isDemo, setIsDemo] = useState(false);
  const [notification, setNotification] = useState(null);

  // AI Modal state
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [aiResult, setAiResult] = useState(null);
  const [isAILoading, setIsAILoading] = useState(false);

  // Initial load: Load baseline OpenAPI specification and documented inventory
  useEffect(() => {
    fetchHealth().then(setHealth);
    initBaseline();
  }, []);

  const showNotification = (msg) => {
    setNotification(msg);
    setTimeout(() => {
      setNotification((curr) => (curr === msg ? null : curr));
    }, 6000);
  };

  const initBaseline = async () => {
    try {
      // 1. Preload baseline specification file in Box 1
      const demoFiles = await fetchDemoFiles();
      const sFile = new File([demoFiles.spec_content], demoFiles.spec_filename, {
        type: 'text/yaml',
      });
      setSpecFile(sFile);
      setIsDemo(true);

      // 2. Load baseline documented scan results
      const baseline = await fetchBaselineScan();
      setScanResult(baseline);
      showNotification('📋 Baseline OpenAPI specification loaded with documented inventory. Ingest traffic to scan for anomalies.');
    } catch (err) {
      console.warn('Could not initialize baseline scan:', err);
    }
  };

  const handleLoadDemo = async () => {
    setIsLoading(true);
    setScanError(null);
    try {
      const demoFiles = await fetchDemoFiles();
      const sFile = new File([demoFiles.spec_content], demoFiles.spec_filename, {
        type: 'text/yaml',
      });
      const tFile = new File([demoFiles.traffic_content], demoFiles.traffic_filename, {
        type: 'application/json',
      });
      setSpecFile(sFile);
      setTrafficFile(tFile);
      setIsDemo(true);

      showNotification('⚡ Demo traffic batch loaded into Box 2! Click "Run Security Scan" to analyze.');
    } catch (err) {
      setScanError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilesScan = async (sFile, tFile) => {
    const fileToScanSpec = sFile || specFile;
    const fileToScanTraffic = tFile || trafficFile;

    if (!fileToScanSpec || !fileToScanTraffic) {
      setScanError('Please select or load both an OpenAPI specification file and a traffic JSON file.');
      return;
    }

    setIsLoading(true);
    setScanError(null);
    try {
      let data;
      if (isDemo && fileToScanSpec.name === 'openapi.yaml' && fileToScanTraffic.name === 'traffic.json') {
        data = await runDemoScan();
      } else {
        data = await runScanWithFiles({
          specFile: fileToScanSpec,
          trafficFile: fileToScanTraffic,
        });
      }

      // Tag ONLY the primary newly detected shadow endpoint with the LATEST badge
      let taggedFindingOnce = false;
      const enhancedFindings = (data.findings || []).map((f) => {
        if (!taggedFindingOnce && (f.path.includes('/admin') || f.type === 'SHADOW_ENDPOINT')) {
          taggedFindingOnce = true;
          return { ...f, is_latest: true };
        }
        return f;
      });

      // Pin the newly scanned finding to the top
      enhancedFindings.sort((a, b) => (b.is_latest ? 1 : 0) - (a.is_latest ? 1 : 0));

      let taggedInventoryOnce = false;
      const enhancedInventory = (data.inventory || []).map((item) => {
        if (!taggedInventoryOnce && (item.endpoint.includes('/admin') || item.status === 'SHADOW')) {
          taggedInventoryOnce = true;
          return { ...item, is_latest: true };
        }
        return item;
      });

      setScanResult({
        ...data,
        findings: enhancedFindings,
        inventory: enhancedInventory,
      });

      showNotification(`🛡️ Scan completed! Newly detected endpoint [GET /admin/users] added with the LATEST tag.`);
    } catch (err) {
      setScanError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setSpecFile(null);
    setTrafficFile(null);
    setIsDemo(false);
    setScanResult(null);
    setScanError(null);
    showNotification('Cleared active files and findings. Select custom files or click "Load Demo Data".');
  };

  const handleSetSpecFile = (file) => {
    setSpecFile(file);
    setIsDemo(false);
    if (file) {
      showNotification(`Selected specification: ${file.name}`);
    }
  };

  const handleSetTrafficFile = (file) => {
    setTrafficFile(file);
    setIsDemo(false);
    if (file) {
      showNotification(`Selected traffic batch: ${file.name}`);
    }
  };

  const handleOpenAI = async (finding) => {
    setSelectedFinding(finding);
    setAiResult(null);
    setIsAILoading(true);
    try {
      const result = await analyzeFindingWithAI(finding);
      setAiResult(result);
    } catch (err) {
      setAiResult({
        provider: 'fallback',
        model: 'rule-engine',
        explanation: `Analysis error: ${err.message}`,
        security_impact: 'Check server logs.',
        recommended_remediation: 'Inspect endpoint manually.',
        should_add_to_openapi: false,
      });
    } finally {
      setIsAILoading(false);
    }
  };

  const handleCloseAI = () => {
    setSelectedFinding(null);
    setAiResult(null);
  };

  return (
    <div className="app-container">
      <Header systemHealth={health} />

      <ScanInterface
        specFile={specFile}
        trafficFile={trafficFile}
        isDemo={isDemo}
        scanSummary={scanResult?.summary}
        onSetSpecFile={handleSetSpecFile}
        onSetTrafficFile={handleSetTrafficFile}
        onRunDemo={handleLoadDemo}
        onRunFiles={handleFilesScan}
        onClear={handleClear}
        isLoading={isLoading}
        error={scanError}
        notification={notification}
      />

      {!scanResult ? (
        <div className="empty-scan-state">
          <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🛡️</div>
          <h3>No Active Scan Results</h3>
          <p>
            Click <strong style={{ color: '#c4b5fd' }}>"⚡ Load Demo Data"</strong> above or select your OpenAPI spec and traffic JSON files, then click <strong style={{ color: '#38bdf8' }}>"🛡️ Run Security Scan"</strong>.
          </p>
        </div>
      ) : (
        <div id="scan-results-section">
          <div className="results-header">
            <div className="section-title">
              <span>📊</span>
              <span>Security Audit & Scan Results</span>
              <span className={`badge-live-scan risk-${scanResult.summary?.risk_level || 'CLEAN'}`}>
                {scanResult.summary?.risk_level} RISK ({scanResult.summary?.risk_score}/100)
              </span>
            </div>
            <div className="results-subtext">
              Active Evaluation: {scanResult.summary?.total_observed_endpoints || 0} Observed • {scanResult.summary?.shadow_endpoints || 0} Shadow Endpoints • {scanResult.findings?.length || 0} Findings
            </div>
          </div>

          <SummaryCards summary={scanResult?.summary} />

          <div className="content-layout">
            <MainFindingPanel
              findings={scanResult?.findings || []}
              onSelectAI={handleOpenAI}
            />

            <EndpointInventory
              inventory={scanResult?.inventory || []}
            />
          </div>
        </div>
      )}

      {selectedFinding && (
        <AIModal
          finding={selectedFinding}
          aiResult={aiResult}
          isLoading={isAILoading}
          onClose={handleCloseAI}
        />
      )}
    </div>
  );
}
