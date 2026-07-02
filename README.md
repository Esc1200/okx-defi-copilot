# DeFi Copilot

Your AI-Powered DeFi Research Agent. Scans protocols across 7 major chains, scores risk, analyzes yield opportunities, and generates actionable research reports.

**OKX.AI Genesis Hackathon — Finance Copilot Track**

## What it does

1. **Yield Scanning** — Fetches live pool data from DeFiLlama across all major chains
2. **Risk Scoring** — Scores every protocol on 5 dimensions (TVL, trend, audits, exploits, age)
3. **Opportunity Ranking** — Ranks yields by a composite score (APY × safety)
4. **Insight Generation** — Identifies best risk-adjusted yields, safest protocols, red flags
5. **X Post Generation** — Auto-generates research posts for social sharing

## Supported Chains

Ethereum, Arbitrum, Base, Optimism, Mantle, Polygon, BSC

## Usage

```bash
# Full research sweep (all chains)
python copilot.py

# Focus on one chain
python copilot.py --chain ethereum
python copilot.py --chain arbitrum
python copilot.py --chain mantle

# Top 5 opportunities only
python copilot.py --top 5

# Risk scoring only
python copilot.py --risk-only

# Generate X post
python copilot.py --x-post

# JSON output for integration
python copilot.py --json
```

## Example Output

```
═════════════════════════════════════════════════════════════════
  DEFI COPILOT — RESEARCH REPORT
  2026-07-02 23:04 UTC | Chain: ALL
═════════════════════════════════════════════════════════════════

📊 ECOSYSTEM OVERVIEW
  Active Pools:     2,847
  Total TVL:        $45,200,000,000
  Average APY:      8.45%
  Stablecoin Pools: 23.1%

🏆 TOP YIELD OPPORTUNITIES
  #    Symbol               Protocol            APY            TVL  Risk
  1    USDe                 Ethena            12.50%    $45,000,000  🟢
  2    sUSDe                Aave V3            5.80%   $179,000,000  🟢
  3    USDY                 Ondo               5.20%    $28,700,000  🟢

🛡️ PROTOCOL RISK SCORES
  Protocol                      TVL  Score      Label  Category
  Aave V3             $12,462,327,587    71    MEDIUM    Lending
  Uniswap V3           $1,424,739,454    71    MEDIUM    DEX
  Compound V3          $1,095,514,123    71    MEDIUM    Lending

💡 INSIGHTS
  • Safest protocols: Aave V3, Compound V3, Uniswap V3
  • Best stablecoin yield: sUSDe on Aave V3 at 5.80% APY
  • Caution: 12 protocols have declining TVL
```

## How it works

The agent uses DeFiLlama's public API (no API key needed) to fetch:
- Live pool data (APY, TVL, stability, IL risk)
- Protocol metadata (audits, category, chain deployment, TVL history)

Risk scores are computed from 5 weighted dimensions:
- **TVL Size** (0-20): Higher TVL = more battle-tested
- **TVL Trend** (0-20): Growing vs declining over 30 days
- **Audit Coverage** (0-20): Number and quality of audits
- **Exploit History** (0-20): Past security incidents
- **Protocol Age** (0-20): Time since deployment

## Requirements

```
requests>=2.28.0
```

## License

MIT
