# Contributing to API Sentinel

Thank you for your interest in contributing to **API Sentinel**! We welcome contributions from developers and cybersecurity researchers of all skill levels.

---

## Code of Conduct
We are committed to providing a friendly, safe, and welcoming environment for all participants. Please treat everyone with respect and empathy.

---

## Development Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & npm
- (Optional) **Ollama** for local AI testing (`ollama run gemma:2b`)

### Clone the Repository
```bash
git clone https://github.com/your-username/api-sentinel.git
cd api-sentinel
```

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## Git Workflow
1. Fork the repo and create your branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Follow Conventional Commits:
   - `feat: add CSV traffic parser`
   - `fix: handle trailing slashes in path normalizer`
   - `docs: add Ollama setup guide`
   - `test: add drift detector edge cases`
3. Run tests before submitting:
   ```bash
   pytest backend/tests
   ```
4. Push your branch and open a Pull Request.

---

## Contributor-Friendly Issues

Looking for somewhere to start? Check out these "Good First Issues":

- [ ] **Add CSV traffic parser**: Ingest traffic logs formatted as CSV.
- [ ] **Add Nginx / Apache log parser**: Parse raw combined access logs into API Sentinel requests.
- [ ] **Add more OpenAPI edge-case tests**: Expand tests for polymorphic schemas and oneOf/anyOf.
- [ ] **Add endpoint filtering**: Filter findings by severity (Critical/High/Medium/Low) in the UI.
- [ ] **Add SARIF export**: Export scan findings into SARIF for GitHub Security tab integration.
- [ ] **Improve dashboard charts**: Add latency or method distribution visual breakdown using Recharts.
- [ ] **Add FastAPI traffic middleware**: Middleware to log live traffic directly to API Sentinel.
- [ ] **Add Flask middleware**: Lightweight interceptor for Flask apps.
- [ ] **Add Express middleware**: Node.js/Express traffic collector.
- [ ] **Add OpenAPI 3.1 support**: Add JSON Schema 2020-12 dialect support.
- [ ] **Improve Ollama prompts**: Refine prompts for lower latency and sharper security recommendations.
- [ ] **Add GitHub Action security report**: Action that comments findings directly on PRs.
