# Contributing to API Sentinel

We love your input! We want to make contributing to API Sentinel as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

---

## Quick Workflow

### 1. Clone the repository
```bash
git clone https://github.com/your-username/api-sentinel.git
cd api-sentinel
```

### 2. Create a topic branch
```bash
git checkout -b feat/add-shadow-detector-rule
```

### 3. Make changes and run tests
```bash
# Backend tests
pytest backend/tests

# Frontend build check
cd frontend && npm run build
```

### 4. Commit your changes
Use Conventional Commits:
```bash
git commit -m "feat: add shadow endpoint detector"
git commit -m "fix: normalize numeric path parameters"
git commit -m "docs: improve contribution guide"
git commit -m "test: add detector coverage"
```

### 5. Create a Pull Request
Push your branch to GitHub and submit a Pull Request describing your changes and linking to any relevant issues.

---

## Good First Issues for Hackathon & Open Source Contributors

The following tasks are scoped to be beginner-friendly and modular:

- **Add CSV traffic parser**: Ingest observed requests from CSV logs.
- **Add Nginx log parser**: Parse standard Nginx/Apache access log formats into `TrafficRequest` models.
- **Add more OpenAPI tests**: Expand edge case coverage for complex `$ref` references.
- **Add endpoint filtering**: Search/filter the dashboard Endpoint Inventory table by method or status.
- **Add SARIF export**: Export scan findings into SARIF for GitHub Advanced Security ingestion.
- **Improve dashboard charts**: Add interactive visual breakdown with Recharts.
- **Add FastAPI traffic middleware**: A drop-in Python middleware to automatically stream requests to API Sentinel.
- **Add Flask middleware**: Interceptor for Flask microservices.
- **Add Express middleware**: Node.js/Express traffic collector.
- **Add OpenAPI 3.1 support**: Full support for JSON Schema 2020-12 dialect keywords.
- **Improve Ollama prompts**: Provide few-shot examples for localized LLMs.
- **Add GitHub Action security report**: Post formatted Markdown PR comments with drift detection results.
