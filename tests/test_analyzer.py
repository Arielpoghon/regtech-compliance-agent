"""Unit tests for the RegTech analyzer (stdlib unittest, no dependencies).

Run:  python3 -m unittest tests/test_analyzer.py -v   (or python3 -m unittest discover tests)
"""
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "backend"))

from main import analyze_source, fallback_report, JURISDICTIONS  # noqa: E402

OFAC_ADDR = "0x8576acc5C05D6Ce88F4e49bF65bDf0C62F91353C"  # Tornado Cash: Proxy (OFAC-designated)

RISKY = """// SPDX-License-Identifier: MIT
contract RiskyToken {
    address public owner;
    mapping(address => bool) public blacklist;
    bool public paused;
    function mint(address to) external { require(msg.sender == owner); }
    function upgradeTo(address i) external { require(msg.sender == owner); }
    function rescue() external { require(msg.sender == owner); }
    function withdraw() external {
        (bool ok,) = msg.sender.call{value: address(this).balance}("");
        require(ok);
    }
}"""

CLEAN = """// SPDX-License-Identifier: MIT
contract CompliantRWA {
    address public admin; address public timelock; address public multisig;
    mapping(address => bool) public kycVerified;
    mapping(address => bool) public transferAllowed;
    bool public paused;
    function noop() external {}
}"""

USDT_LIKE = """contract TetherToken {
    address public owner; bool public paused;
    mapping(address => bool) public blacklist;
    mapping(address => bool) public whitelist;
    function issue(uint256 amt) public { owner.issue(amt); }
    function pause() public { require(owner == msg.sender); paused = true; }
}"""


class TestAnalyzer(unittest.TestCase):
    def test_risky_scores_high(self):
        a = analyze_source(RISKY)
        self.assertEqual(a["risk_level"], "HIGH")
        self.assertGreaterEqual(a["risk_score"], 60)

    def test_risky_flags_unilateral_mint(self):
        a = analyze_source(RISKY)
        self.assertIn("unilateral minting without timelock/multisig", a["risk_reasons"])

    def test_risky_flags_reentrancy(self):
        a = analyze_source(RISKY)
        self.assertIn("reentrancy-prone external call", a["risk_reasons"])

    def test_clean_scores_low(self):
        a = analyze_source(CLEAN)
        self.assertEqual(a["risk_level"], "LOW")
        self.assertLess(a["risk_score"], 30)

    def test_comments_are_stripped(self):
        commented = "// mint(owner) blacklist upgrade\n" + "contract C {}"
        a = analyze_source(commented)
        self.assertEqual(a["patterns"], {})

    def test_ofac_address_flags_sanctioned_hit(self):
        src = 'contract C { address public treasury = ' + OFAC_ADDR + "; }"
        a = analyze_source(src)
        self.assertEqual([h.lower() for h in a["sanctioned_hits"]], [OFAC_ADDR.lower()])
        self.assertGreaterEqual(a["risk_score"], 50)
        self.assertTrue(any(r.startswith("sanctioned address referenced") for r in a["risk_reasons"]))

    def test_address_dedupe(self):
        src = 'contract C { address a = ' + OFAC_ADDR + '; address b = ' + OFAC_ADDR + '; }'
        a = analyze_source(src)
        self.assertEqual(len(a["addresses_found"]), 1)

    def test_no_owner_no_mint_flags(self):
        a = analyze_source("contract Neutral { function go() external {} }")
        self.assertEqual(a["risk_score"], 0)
        self.assertEqual(a["risk_level"], "LOW")

    def test_usdt_like_blacklist_without_kyc(self):
        a = analyze_source(USDT_LIKE)
        self.assertIn("blacklist without KYC gating", a["risk_reasons"])
        self.assertEqual(a["risk_level"], "LOW")

    def test_multisig_mitigates_mint_risk(self):
        mitigated = RISKY.replace("address public owner;",
                                  "address public owner; address public multisig;")
        a = analyze_source(mitigated)
        self.assertNotIn("unilateral minting without timelock/multisig", a["risk_reasons"])

    def test_risk_score_capped_at_100(self):
        src = RISKY + "\n// address: " + OFAC_ADDR
        a = analyze_source(src)
        self.assertEqual(a["risk_score"], 100)
        self.assertEqual(a["risk_level"], "CRITICAL")

    def test_fallback_report_mentions_jurisdiction(self):
        a = analyze_source(RISKY)
        r = fallback_report(a, JURISDICTIONS["EU"])
        self.assertIn("European Union (MiCA)", r)
        self.assertIn("Risk level", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
