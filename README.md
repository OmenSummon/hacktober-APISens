<div align="center">

# 🛡️ API Sentinel
### AI-Powered API Drift & Shadow Endpoint Detector

[![Tests](https://github.com/hacktober/actions/workflows/tests.yml/badge.svg)](https://github.com/hacktober/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React: 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![OWASP API Security](https://img.shields.io/badge/OWASP-API9%20%7C%20API8-red.svg)](https://owasp.org/www-project-api-security/)

**Compare declared OpenAPI specifications against live API traffic to detect shadow endpoints, schema drift, and security misconfigurations before attackers exploit them.**

[Problem](#problem-statement) • [Architecture](#architecture) • [Features](#core-features) • [Quickstart](#quickstart) • [Demo Mode](#demo-mode) • [Documentation](#api-documentation) • [Roadmap](#roadmap)

</div>

---

## 📌 Problem Statement

Modern development teams declare their intended API contract using OpenAPI / Swagger specifications. However, in production and staging environments, reality quickly drifts:
- **Shadow Endpoints**: Developers deploy internal, test, or experimental routes (e.g. `/admin/users`, `/debug`) that never get documented.
- **API Drift**: Production traffic receives unexpected query parameters, undocumented HTTP verbs, or unvalidated request body fields (e.g. `coupon` on checkout).
- **Security Misconfigurations**: Protected routes fail to enforce authentication, or diagnostic utilities leak internal application state.

According to the **OWASP API Security Top 10 (2023)**:
- **API9: Improper Inventory Management** is among the most pervasive vectors for data breaches.
- **API8: Security Misconfiguration** leaves debug endpoints and excessive permissions exposed.

**API Sentinel** solves this by continuously contrasting declared API specifications with observed network traffic, scoring security risk deterministically, and suggesting actionable OpenAPI remediation patches.

---

## 🏗️ Architecture

```
                               ┌─────────────────────────────┐
                               │  OpenAPI 3.x Specification  │
                               │        (YAML / JSON)        │
                               └──────────────┬──────────────┘
                                              │
┌─────────────────────────────┐               ▼
│    Observed API Traffic     │────►┌─────────────────────────────┐
│      (JSON / Logs)          │     │    OpenAPI Parser &         │
└──────────────┬──────────────┘     │   Path Parameter Normalizer │
               │                    └──────────────┬──────────────┘
               ▼                                   │
┌──────────────────────────────────────────────────┴──────────────┐
│                    Detection & Risk Engine                      │
│                                                                 │
│  ├─ Shadow Endpoint Detector   (OWASP API9: Missing Endpoints)  │
│  ├─ Method & Parameter Drift   (OWASP API9: Extra Verbs/Params) │
│  ├─ Request Schema Drift       (OWASP API3: Mass Assignment)    │
│  ├─ Auth Mismatch Detector     (OWASP API8: Security Bypass)    │
│  └─ Deterministic Risk Scorer  (OWASP-weighted 0-100 score)     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│   Local AI Security Advisor │ │   OpenAPI Remediation       │
│    (Ollama / Gemma / Llama) │ │  YAML Diff & Patch Engine   │
│  + Deterministic Fallback   │ │ (Never auto-mutates spec)   │
└──────────────┬──────────────┘ └──────────────┬──────────────┘
               │                               │
               └───────────────┬───────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│               React Dark SOC Security Operations Dashboard       │
│                & REST API / Swagger UI (/docs) / CLI            │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Core Features

1. **OpenAPI 3.x Ingestion**: Full YAML/JSON parsing resolving routes, HTTP methods, parameters, request body schemas, and authentication schemes.
2. **Observed Traffic Ingestion**: Batch ingestion endpoint (`POST /api/traffic`) supporting file uploads or streaming JSON payloads.
3. **Intelligent Path Normalization**: Matches parameterized templates (`/users/{id}`) and heuristically normalizes dynamic numeric IDs, UUIDs, and Mongo ObjectIDs while protecting static keywords (`/admin`, `/debug`, `/v1`).
4. **Shadow Endpoint Detection**: Pinpoints undocumented endpoints receiving active requests with severity ratings and traffic volume indicators.
5. **Multi-Vector API Drift Detection**: Flags undocumented HTTP verbs, extra query parameters, and unvalidated request body properties.
6. **Deterministic Risk Scoring**: Formula-based risk score (0–100) and qualitative levels (`CLEAN`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) with transparent mathematical calculation.
7. **Local AI Analysis (Ollama)**: Enriches findings with root cause explanations, OWASP security implications, and remediation steps. Operates with an infallible offline deterministic fallback if Ollama is not installed.
8. **OpenAPI Remediation Patches**: Generates valid OpenAPI 3.0 YAML diff snippets for discovered endpoints so teams can update their specifications.

---

## 🔒 OWASP API Security Top 10 Mapping

| OWASP Category | Vulnerability Detected | Risk Level |
| :--- | :--- | :--- |
| **API9:2023 Improper Inventory Management** | Undocumented shadow routes (`/admin/users`, `/debug`) | **HIGH / CRITICAL** |
| **API9:2023 Improper Inventory Management** | Undocumented query parameters (`role`, `show_deleted`) | **MEDIUM** |
| **API8:2023 Security Misconfiguration** | Unauthenticated access to protected routes | **HIGH** |
| **API3:2023 Broken Object Property Level Authorization** | Undocumented request body properties (`coupon` field drift) | **MEDIUM** |

---

## 🚀 Quickstart

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & npm
- (Optional) **Ollama** for local LLM inference

### 1. Clone the Repository
```bash
git clone https://github.com/hacktober/api-sentinel.git
cd api-sentinel
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API Sentinel Backend is running at: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Interactive ReDoc: `http://localhost:8000/redoc`

### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
- Open your browser at: `http://localhost:5173`

---

## 🧪 Running Tests

The test suite covers normalization, parsing, shadow detection, drift detection, risk scoring, remediation, and API endpoints.

```bash
cd backend
pytest -v
```

All 22+ tests run in seconds without external dependencies.

---

## 🎬 Demo Mode (One-Click Evaluation)

Judge and evaluator friendly! You do not need to prepare real API traffic to test the tool:
1. Open the dashboard at `http://localhost:5173`.
2. Click the **"⚡ Load Demo Data"** button.
3. The dashboard instantly evaluates realistic pre-packaged specifications and traffic:
   - **Documented**: `GET /users`, `POST /users`, `GET /users/{id}`, `GET /products`, `POST /orders`
   - **Detected Shadow Endpoints**: `GET /admin/users` (HIGH/CRITICAL), `GET /debug` (CRITICAL)
   - **Detected Schema Drift**: `POST /orders` (Undocumented `coupon` field)
   - **Detected Parameter Drift**: `GET /users` (Undocumented `role`, `show_deleted` params)
4. Click **"✨ AI Analysis & Patch"** on any finding to view the root-cause reasoning and copy the generated OpenAPI remediation YAML.

---

## 🤖 Local AI Setup (Optional)

API Sentinel is built with **zero external AI dependencies**. If Ollama is offline or unavailable, the built-in deterministic security advisor functions without interruption.

To enable local LLM reasoning:
1. Install [Ollama](https://ollama.ai).
2. Pull a lightweight model:
   ```bash
   ollama pull gemma:2b
   # or: ollama pull llama3
   ```
3. Ensure Ollama is running (`ollama serve`). API Sentinel will automatically detect the local daemon and use it for enriched analysis.

---

## 📡 API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root service meta and OWASP mapping |
| `GET` | `/api/health` | Health status and AI provider status |
| `POST` | `/api/openapi/parse` | Parse and normalize an OpenAPI 3.x YAML/JSON spec |
| `POST` | `/api/traffic` | Ingest observed API traffic batch |
| `GET` | `/api/traffic` | Retrieve stored traffic sample |
| `POST` | `/api/scan` | Run security comparison against specification & traffic |
| `POST` | `/api/demo` | Instantly trigger scan using pre-configured demo datasets |
| `GET` | `/api/findings` | Query and filter security findings by severity |
| `POST` | `/api/ai/analyze` | Request deep AI security analysis for a finding |
| `POST` | `/api/ai/patch` | Generate OpenAPI 3.0 remediation patch YAML |

---

## 💻 CLI Usage

You can also run scans directly in CI/CD pipelines or terminals via the Typer CLI:

```bash
cd backend
python -m app.cli scan --demo
# Or with custom files:
python -m app.cli scan --spec ../examples/sample-openapi.yaml --traffic ../examples/sample-traffic.json
```

---

## 🤝 Contributing

Contributions are warmly welcomed! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/contributing.md](docs/contributing.md) for guidelines, code style, and starter issues.

---

## 🗺️ Roadmap

- [x] OpenAPI 3.x YAML/JSON parser
- [x] Dynamic path parameter normalization
- [x] Shadow endpoint detection
- [x] Parameter & Request body schema drift detection
- [x] Deterministic OWASP-weighted risk scoring
- [x] React Dark SOC Security Operations Dashboard
- [x] Local Ollama integration with infallible offline fallback
- [x] OpenAPI YAML remediation patch generator
- [ ] Nginx & Apache access log parser
- [ ] SARIF report export for GitHub Advanced Security
- [ ] Drop-in FastAPI & Express traffic middleware
- [ ] Real-time WebSocket streaming traffic monitor

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
