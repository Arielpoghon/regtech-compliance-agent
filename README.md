# RegTech AI Compliance Agent

**BLI Legal Tech Hackathon 2** — LegalTech & RegTech track

An AI-powered compliance agent for smart contracts and RWA tokens. Given a
contract address or source code, it produces a jurisdiction-aware compliance
report: sanctions screening, KYC/AML surface, legal-document attestations,
and a risk score — all in one click.

## Stack
- Backend: Python 3.14 + FastAPI + OpenAI-compatible LLM (local or API)
- Frontend: single-page HTML/JS (no build step) — demo-ready
- Analysis: Solidity AST heuristics + LLM reasoning + sanctions-list matching

## Run
```
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000
# open frontend/index.html
```

## Demo flow (3 min)
1. Paste a contract address or upload Solidity source
2. Pick a jurisdiction (US/EU/SG/UAE)
3. Get a compliance report with risk score, sanctions hits, KYC gaps, attestations
