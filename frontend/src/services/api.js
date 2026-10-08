const API_BASE = '/api';

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed (${res.status})`);
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function runDemoScan() {
  const res = await fetch(`${API_BASE}/demo`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Demo scan failed');
  }
  return await res.json();
}

export async function fetchDemoFiles() {
  const res = await fetch(`${API_BASE}/demo/files`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch demo files');
  }
  return await res.json();
}

export async function fetchBaselineScan() {
  const res = await fetch(`${API_BASE}/demo/baseline`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch baseline scan');
  }
  return await res.json();
}



export async function runScanWithPayload({ specText, trafficList }) {
  const res = await fetch(`${API_BASE}/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      openapi_spec: specText,
      traffic: trafficList,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Security scan failed');
  }
  return await res.json();
}

export async function runScanWithFiles({ specFile, trafficFile }) {
  const formData = new FormData();
  if (specFile) formData.append('spec_file', specFile);
  if (trafficFile) formData.append('traffic_file', trafficFile);

  const res = await fetch(`${API_BASE}/scan`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'File security scan failed');
  }
  return await res.json();
}

export async function analyzeFindingWithAI(finding) {
  const res = await fetch(`${API_BASE}/ai/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ finding }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'AI analysis request failed');
  }
  return await res.json();
}
