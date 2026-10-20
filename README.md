# RegTech AI Compliance Agent

**BLI Legal Tech Hackathon 2** — LegalTech & RegTech track

An AI-powered compliance agent for smart contracts and RWA tokens. Paste
Solidity source, pick a jurisdiction (US / EU / SG / UAE), and get a
compliance report in seconds: sanctions screening, KYC/AML posture,
legal-document attestations, and a risk score.

> **What it is, honestly:** a deterministic heuristic analyzer (14
> compliance-relevant regex/semantic patterns over comment-stripped source)
> plus a sanctions-address screen, with an optional LLM pass for prose.
> It is a first-pass triage tool, not a substitute for a full audit.

## Try it now

- **Live demo (works offline, no backend needed):**
  https://regtech-compliance-agent.netlify.app/
  Click **Load risky contract → Analyze** and **Load clean contract →
  Analyze** for the side-by-side comparison.
- **Backend (optional):** `python3 backend/main.py` — pure stdlib, no
  third-party install. Serves `POST /analyze`, `GET /health`,
  `GET /jurisdictions` on port 8000 (CORS enabled).
- **Tests:** `python3 tests/test_analyzer.py` → 12/12 pass.

## Stack

- **Backend:** Python 3.14, standard library only (`http.server` +
  `socketserver`). No third-party dependencies. Set `OPENAI_API_KEY` to get
  LLM-written reports; without it you get the deterministic fallback report.
- **Frontend:** single self-contained HTML/JS page (Tailwind + marked via
  CDN). The analyzer is ported 1:1 from the Python backend, so the deployed
  static site performs the full analysis **in the browser** — the "Analyze"
  button works with zero servers.

## Evidence (real mainnet contracts)

Analyzed with this exact repo code on Sourcify-verified sources
(see [docs/EVIDENCE.md](docs/EVIDENCE.md) for the full run):

| Contract | Risk | Level | Verdict |
|---|---:|---|---|
| WETH9 `0xC02a…6Cc2` | 0/100 | LOW | correct (no admin surface) |
| DAI `0x6B17…1d0F` | 0/100 | LOW | correct |
| USDT `0xdAC1…1ec7` | 10/100 | LOW | blacklist/pause noted |
| USDC (FiatTokenProxy) `0xA0b8…eB48` | 45/100 | MEDIUM | upgradeable-without-timelock (true positive) |
| UniswapV2Router02 `0x7a25…488D` | 55/100 | MEDIUM | known false-positive class (LP mint/burn) |

Sanctions screening: embedded OFAC slice flagged the Tornado Cash proxy
address in a controlled test (unit test); 0 sanctioned addresses among the
extracted literals of the five mainnet sources above.

## Demo flow (3 min)

1. Paste a contract (or load the two built-in samples)
2. Pick a jurisdiction (US/EU/SG/UAE)
3. Read the report: risk score + reasons, sanctions hits, KYC posture,
   attestations, recommendations — then repeat for the clean sample

Video: https://youtu.be/_RxSDvYMz58

## Limitations

- It detects *code patterns*, not intent: proxies with LP-style mint/burn
  and role-based `owner` naming can produce false positives; the reason list
  is always shown so a reviewer can check what fired.
- The embedded sanctions list is a small OFAC slice for demo purposes;
  production use needs the full feed.
- No AST analysis, no bytecode verification, no simulation.

## License

MIT — see [LICENSE](LICENSE).
