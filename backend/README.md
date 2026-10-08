# API Sentinel — Backend

The backend engine for API Sentinel is built with **FastAPI**, **Pydantic**, and **Pytest**. It provides real-time OpenAPI specification parsing, traffic normalization, shadow endpoint detection, schema drift identification, deterministic risk scoring, and optional local AI enrichment via Ollama.

---

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entrypoint & middleware
│   ├── config.py            # Environment configurations (Pydantic BaseSettings)
│   ├── cli.py               # Typer CLI for terminal scanning
│   ├── models/              # Pydantic schemas for Specs, Traffic, Findings
│   │   ├── openapi.py
│   │   ├── traffic.py
│   │   ├── findings.py
│   │   └── scan.py
│   ├── services/            # Core business logic
│   │   ├── normalizer.py     # Path parameter normalization regex engine
│   │   ├── openapi_parser.py # OpenAPI 3.x YAML/JSON parser
│   │   ├── traffic_service.py# In-memory traffic store & ingestion
│   │   ├── remediation.py    # OpenAPI patch / diff generator
│   │   └── demo_data.py      # Built-in demo datasets
│   ├── detectors/           # Security detection engines
│   │   ├── shadow_detector.py# Shadow endpoint detector (OWASP API9)
│   │   ├── drift_detector.py # Parameter & schema drift detector
│   │   └── risk_scorer.py    # Deterministic OWASP-aligned risk scoring
│   ├── ai/                  # AI layer
│   │   └── ollama_client.py  # Local Ollama client with deterministic fallback
│   └── routes/              # FastAPI APIRouters
│       ├── health.py        # /api/health
│       ├── openapi.py       # /api/openapi/parse
│       ├── traffic.py       # /api/traffic
│       ├── scan.py          # /api/scan
│       ├── findings.py      # /api/findings
│       └── ai.py            # /api/ai/analyze
├── tests/                   # Pytest test suite (>10 comprehensive tests)
└── requirements.txt
```

---

## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the test suite
pytest -v

# 3. Start the development server
uvicorn app.main:app --reload --port 8000
```

Interactive Swagger documentation is available at `http://localhost:8000/docs`.
Interactive ReDoc documentation is available at `http://localhost:8000/redoc`.

---

## CLI Usage

API Sentinel also includes a fast terminal CLI:

```bash
python -m app.cli scan --spec ../examples/sample-openapi.yaml --traffic ../examples/sample-traffic.json
```
