import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import SummaryCards from '../components/SummaryCards';
import ScanInterface from '../components/ScanInterface';
import MainFindingPanel from '../components/MainFindingPanel';
import EndpointInventory from '../components/EndpointInventory';
import AIModal from '../components/AIModal';
import {
  analyzeFindingWithAI,
  fetchHealth,
  runDemoScan,
  runScanWithFiles,
} from '../services/api';

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [scanError, setScanError] = useState(null);

  // AI Modal state
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [aiResult, setAiResult] = useState(null);
  const [isAILoading, setIsAILoading] = useState(false);

  // Initial load
  useEffect(() => {
    fetchHealth().then(setHealth);
    // Automatically run demo scan so dashboard opens with live data!
    handleDemoScan();
  }, []);

  const handleDemoScan = async () => {
    setIsLoading(true);
    setScanError(null);
    try {
      const data = await runDemoScan();
      setScanResult(data);
    } catch (err) {
      setScanError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilesScan = async (specFile, trafficFile) => {
    setIsLoading(true);
    setScanError(null);
    try {
      const data = await runScanWithFiles({ specFile, trafficFile });
      setScanResult(data);
    } catch (err) {
      setScanError(err.message);
    } finally {
      setIsLoading(false);
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

      <SummaryCards summary={scanResult?.summary} />

      <ScanInterface
        onRunDemo={handleDemoScan}
        onRunFiles={handleFilesScan}
        isLoading={isLoading}
        error={scanError}
      />

      <div className="content-layout">
        <MainFindingPanel
          findings={scanResult?.findings || []}
          onSelectAI={handleOpenAI}
        />

        <EndpointInventory
          inventory={scanResult?.inventory || []}
        />
      </div>

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
