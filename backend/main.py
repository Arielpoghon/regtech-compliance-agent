"""RegTech AI Compliance Agent — stdlib-only HTTP server (Python 3.14 friendly)."""
import json, os, re, http.server, socketserver, urllib.parse

# Avoid external deps entirely.
import http.client

SANCTIONS = {
    "0x000000000000000000000000000000000000dead",
    "0x8576acc5c05d6ce88f4e49bf65bdf0c62f91353c",
    "0x1da5821544e25c636c1417ba96ffe2dd455e9213",
    "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
}

JURISDICTIONS = {
    "US": {"name": "United States (SEC/FinCEN)", "kyc": "KYC + AML (BSA)", "sanctions": "OFAC SDN", "disclosure": "Securities Act 1933/34", "stablecoin": "GENIUS Act 2025"},
    "EU": {"name": "European Union (MiCA)", "kyc": "KYC + AMLD6", "sanctions": "EU Consolidated List", "disclosure": "MiCA Title III/IV", "stablecoin": "MiCA EMT/ART"},
    "SG": {"name": "Singapore (MAS)", "kyc": "MAS AML/CFT", "sanctions": "UN + MAS", "disclosure": "SFA", "stablecoin": "MAS stablecoin framework"},
    "UAE": {"name": "UAE (VARA/SCA)", "kyc": "VARA AML", "sanctions": "UN + UAE", "disclosure": "VARA rulebook", "stablecoin": "VARA stablecoin rules"},
}

PATTERNS = [
    ("owner", r"\b(owner|admin|governor|operator)\b", "admin control surface"),
    ("pause", r"\b(pause|unpause|paused)\b", "circuit breaker present"),
    ("blacklist", r"\b(blacklist|blocklist|blocked|banned)\b", "address blocking capability"),
    ("whitelist", r"\b(whitelist|allowlist|allowed)\b", "allowlist gating"),
    ("mint", r"\b(mint|Mint)\b", "minting capability"),
    ("burn", r"\b(burn|Burn)\b", "burning capability"),
    ("upgrade", r"\b(upgrade|Upgrade|proxy|Proxy|UUPS)\b", "upgradeable proxy"),
    ("oracle", r"\boracle|Oracle|priceFeed|PriceFeed\b", "external price oracle dependency"),
    ("reentrancy", r"\.call\{value:|\.call\.value\(", "reentrancy-prone external call"),
    ("kyc", r"\b(kyc|KYC|verifyIdentity|identityVerified|isVerified)\b", "KYC hook present"),
    ("transfer_restrict", r"\b(transferRestriction|canTransfer|_beforeTokenTransfer)\b", "transfer restrictions"),
    ("multisig", r"\b(multisig|MultiSig|threshold)\b", "multisig governance"),
    ("timelock", r"\b(timelock|Timelock|delay)\b", "timelock present"),
    ("emergency", r"\b(emergency|Emergency|rescue)\b", "emergency rescue function"),
]


def strip_comments(src):
    src = re.sub(r"//.*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src

def analyze_source(src):
    code = strip_comments(src)
    hits = {}
    for name, pat, desc in PATTERNS:
        m = re.findall(pat, code, re.IGNORECASE)
        if m:
            hits[name] = {"count": len(m), "desc": desc}
    addrs = set(re.findall(r"0x[a-fA-F0-9]{40}", src))
    sanctioned = [a for a in addrs if a.lower() in SANCTIONS]
    risk = 0; reasons = []
    if "mint" in hits and "owner" in hits and "multisig" not in hits and "timelock" not in hits:
        risk += 30; reasons.append("unilateral minting without timelock/multisig")
    if "upgrade" in hits and "timelock" not in hits:
        risk += 20; reasons.append("upgradeable without timelock")
    if "reentrancy" in hits:
        risk += 25; reasons.append("reentrancy-prone external call")
    if "oracle" in hits:
        risk += 10; reasons.append("external oracle dependency")
    if sanctioned:
        risk += 50; reasons.append(f"sanctioned address referenced: {sanctioned}")
    if "blacklist" in hits and "kyc" not in hits:
        risk += 10; reasons.append("blacklist without KYC gating")
    if "emergency" in hits:
        risk += 5; reasons.append("emergency rescue function present")
    risk = min(risk, 100)
    level = "LOW" if risk < 30 else "MEDIUM" if risk < 60 else "HIGH" if risk < 85 else "CRITICAL"
    return {"patterns": hits, "addresses_found": sorted(addrs), "sanctioned_hits": sanctioned,
            "risk_score": risk, "risk_level": level, "risk_reasons": reasons}


def fallback_report(analysis, j):
    rl = analysis["risk_level"]; rs = analysis["risk_score"]
    hits = analysis["patterns"]; sanctioned = analysis["sanctioned_hits"]; reasons = analysis["risk_reasons"]
    lines = []
    lines.append(f"## Summary\nRisk level: **{rl}** (score {rs}/100). Detected {len(hits)} compliance-relevant code patterns. Jurisdiction: {j['name']}.")
    lines.append(f"\n## Sanctions screening\nAddresses found: {len(analysis['addresses_found'])}. Sanctioned hits: {sanctioned if sanctioned else 'none'}. Regime: {j['sanctions']}.")
    lines.append(f"\n## KYC/AML posture\nKYC hook present: {'kyc' in hits}. Transfer restrictions: {'transfer_restrict' in hits}. Blacklist capability: {'blacklist' in hits}. Whitelist gating: {'whitelist' in hits}. Regime: {j['kyc']}.")
    lines.append(f"\n## Legal document attestations\nDisclosure regime: {j['disclosure']}. Stablecoin framework: {j['stablecoin']}. Multisig governance: {'multisig' in hits}. Timelock: {'timelock' in hits}.")
    lines.append("\n## Recommendations")
    if reasons:
        for r in reasons: lines.append(f"- Address: {r}")
    else:
        lines.append("- No high-risk patterns detected; proceed with standard legal review.")
    lines.append("- Obtain legal counsel review before mainnet deployment.")
    lines.append("- Maintain an audit trail of compliance decisions.")
    return "\n".join(lines)


def llm_report(analysis, jurisdiction, source_preview):
    j = JURISDICTIONS[jurisdiction]
    api_key = os.getenv("OPENAI_API_KEY")
    prompt = ("You are a RegTech compliance analyst. Given the analysis and jurisdiction, produce a concise "
              "compliance report (max 400 words) with sections: (1) Summary, (2) Sanctions screening, "
              "(3) KYC/AML posture, (4) Legal document attestations, (5) Recommendations. Be specific.\n\n"
              f"Jurisdiction: {j['name']} (KYC: {j['kyc']}, sanctions: {j['sanctions']}, disclosure: {j['disclosure']}, stablecoin: {j['stablecoin']}).\n"
              f"Analysis: {json.dumps(analysis)[:2000]}\nSource preview: {source_preview[:1200]}")
    if not api_key:
        return fallback_report(analysis, j)
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps({"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}).encode(),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]
    except Exception:
        return fallback_report(analysis, j)


class Handler(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/health":
            self._json({"status": "ok", "service": "regtech-compliance-agent"})
        elif path == "/jurisdictions":
            self._json(JURISDICTIONS)
        else:
            self.send_response(404); self._cors(); self.end_headers()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path != "/analyze":
            self.send_response(404); self._cors(); self.end_headers(); return
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        src = body.get("source", "")
        jur = body.get("jurisdiction", "US")
        if jur not in JURISDICTIONS:
            self._json({"error": f"Unknown jurisdiction: {jur}"}, 400); return
        if len(src) < 10:
            self._json({"error": "Source too short"}, 400); return
        a = analyze_source(src)
        report = llm_report(a, jur, src)
        self._json({"contract_name": body.get("contract_name") or "Unnamed",
                    "jurisdiction": jur, "jurisdiction_info": JURISDICTIONS[jur],
                    "analysis": a, "report": report})

    def _json(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    socketserver.ThreadingTCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(("", port), Handler) as httpd:
        print(f"RegTech agent listening on http://localhost:{port}")
        httpd.serve_forever()
