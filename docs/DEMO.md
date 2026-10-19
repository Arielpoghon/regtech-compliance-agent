# 3-Minute Demo Script — RegTech AI Compliance Agent

## 0:00–0:20 — Problem
"Smart contracts and RWA tokens ship without a compliance review. Legal teams
can't read Solidity; auditors don't check sanctions/KYC. Result: projects
launch with unilateral minting, upgradeable proxies with no timelock, and
sanctioned addresses hardcoded — all discovered after the fact."

## 0:20–0:50 — Solution
"RegTech AI Compliance Agent: paste a contract, pick a jurisdiction (US/EU/SG/UAE),
get a compliance report in seconds. Heuristic pattern detection + LLM reasoning
against the jurisdiction's KYC/AML, sanctions, disclosure, and stablecoin rules."

## 0:50–1:40 — Live demo
1. Load sample contract (RiskyToken) — button.
2. Select EU (MiCA). Click Analyze.
3. Show risk badge: MEDIUM/HIGH, score.
4. Walk through detected patterns: owner, mint, pause, blacklist, upgrade, oracle, reentrancy.
5. Sanctions hits: 0 (or add a sanctioned address to demonstrate).
6. Read 2 lines of the report: recommendations.

## 1:40–2:20 — Jurisdiction switch
Switch to US → re-run → show differing disclosure/stablecoin framing (GENIUS Act vs MiCA).

## 2:20–3:00 — Roadmap & ask
- v0.2: on-chain address resolution (Etherscan), multi-contract dependency graph.
- v0.3: PDF attestation export for legal filing.
- Ask: pilot with one law firm / RWA issuer.

## Submission checklist (DoraHacks)
- [ ] Register on dorahacks.io (free)
- [ ] Create a Build entry under BLI Legal Tech Hackathon 2
- [ ] Title: "RegTech AI Compliance Agent"
- [ ] Track: LegalTech & RegTech
- [ ] Upload 3-min demo video (screen recording of the live demo above)
- [ ] Paste GitHub repo link (or zip)
- [ ] Submit before Nov 1 01:01 UTC
EOF
cat > /home/arielp/Work/hackathon-bli/launch.sh <<'EOF'
#!/usr/bin/env bash
cd "$(dirname "$0")/backend"
python3 main.py
EOF
chmod +x /home/arielp/Work/hackathon-bli/launch.sh
echo "done"