# Evidence — analyzer run on real mainnet contracts

All results below were produced by running the shipped analyzer code
(`backend/main.py`, imported directly) on **verified sources downloaded from
Sourcify** (`https://sourcify.dev/server/v2/contract/1/<address>?fields=all`),
using the source file reported by Sourcify's verification record. Raw
responses: `.evidence/*.v2.json` and `*_result.json`.

Date: 2026-10-20 · Endpoint: Ethereum mainnet (chain 1) · Version: v0.2.1

## Results

| # | Contract | Address | Verified file | Risk | Level | Top signals |
|---|----------|---------|--------------|-----:|-------|-------------|
| 1 | WETH9 | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` | WETH9.sol | **0** | LOW | (no admin patterns) |
| 2 | DAI (dss `dai.sol`) | `0x6B175474E89094C44Da98b954EedeAC495271d0F` | dai.sol | **0** | LOW | whitelist (wards), mint/burn (VAT semantics) |
| 3 | USDT (TetherToken) | `0xdAC17F958D2ee523a2206206994597C13D831ec7` | TetherToken.sol | **10** | LOW | owner ×19, pause ×11, blacklist ×2, whitelist ×6 |
| 4 | USDC (FiatTokenProxy) | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | FiatTokenProxy.sol | **45** | MEDIUM | upgrade ×7, owner ×4, reentrancy-pattern ×1 |
| 5 | UniswapV2Router02 | `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D` | UniswapV2Router02.sol | **55** | MEDIUM | mint ×4, burn ×3, owner ×8, reentrancy-pattern ×1 |

Sourcify match status at scan time: `match` for #1–#5 source
records used (`exact_match` for dai.sol).

## What the score means on these results

- **USDC → MEDIUM 45/100** is a defensible true positive: the analyzed proxy
  file contains the upgrade/admin delegation surface, and USDC remains
  upgradeable without an on-chain timelock (`upgradeable without timelock`).
- **UniswapV2Router02 → MEDIUM 55/100** is a documented false-positive class:
  semantic-level: `mint`/`burn` here are *liquidity-token* semantics (LP
  mint/burn), not unilateral admin minting. The heuristic does not model
  function roles; the report shows the reason list so a human reviewer sees
  exactly what fired.
- **WETH9 / DAI → LOW 0/100**: no admin/mint/upward-privilege surface in the
  analyzed source, consistent with their real-world trust posture. (DAI emits
  `whitelist/mint/burn` tokens — informational only.)
- **USDT → LOW 10/100**: the analyzed implementation freezes transfers and
  has a blacklist; scored only for `blacklist without KYC gating`. Note that
  USDT's actual enforcement lives at the transaction-param level — a static
  approach cannot certify operational behavior.

## Sanctions screening

On the five mainnet sources above, **0 sanctioned addresses** were found
among extracted literals. The sanctions path is exercised in the unit test
`tests/test_analyzer.py::TestAnalyzer.test_ofac_address_flags_sanctioned_hit`,
which embeds the OFAC-designated Tornado Cash: Proxy address
(`0x8576acc5C05D6Ce88F4e49bF65bDf0C62F91353C`): the analyzer flags it with
+50 risk and a deduped, case-insensitive hit.

## Honest limitations

- **Heuristic, not a substitute for audit**: regex per-pattern matching over
  stripped source; no AST/type-system analysis, no bytecode-level
  verification, and no dynamic testing.
- **Sanctions list is a slice**: the sanctions list embedded in this repo is
  a 4-entry slice of the OFAC digital-currency list used for documented demo
  cases; production screening must use the full, updated OFAC feed.
- **Known false-positive classes**: proxies designed with LP mint/burn;
  roles-based functions named `owner`; allowed-list gateways that are
  permissionless under the hood.
- **Solidity v0.4–v0.8 source** covers the analyzed styles; inline asm and
  precompile-style code are not modeled.
