# DeFi Copilot

Your AI-Powered DeFi Research Agent. Scans protocols across chains, scores risk, analyzes yield opportunities, and generates actionable research reports.

**OKX.AI Genesis Hackathon — Finance Copilot Track**

## What it does

1. **Yield Scanning** — Fetches live pool data from DeFiLlama across all major chains
2. **Risk Scoring** — Scores every protocol on 5 dimensions (TVL, trend, audits, exploits, age)
3. **Opportunity Ranking** — Ranks yields by a composite score (APY × safety)
4. **Insight Generation** — Identifies best risk-adjusted yields, safest protocols, red flags
5. **X Post Generation** — Auto-generates research posts for social sharing

## Usage

```bash
# Full research sweep (all chains)
python copilot.py

# Focus on one chain
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
  2026-07-02 18:00 UTC | Chain: MANTLE
═════════════════════════════════════════════════════════════════

📊 ECOSYSTEM OVERVIEW
  Active Pools:     147
  Total TVL:        $140,000,000
  Average APY:      8.45%
  Stablecoin Pools: 23.1%

🏆 TOP YIELD OPPORTUNITIES
  #    Symbol               Protocol            APY            TVL  Risk
  1    USDe                 Ethena            12.50%    $45,000,000  🟢
  2    mETH                 Mantle Staking     8.20%    $32,000,000      
  3    DAI                  Aave V3            5.80%    $28,000,000  🟢

🛡️ PROTOCOL RISK SCORES
  Protocol                      TVL  Score      Label  Category
  Aave V3               $90,000,000    92       LOW    Lending
  Ondo Finance          $28,600,000    85       LOW    RWA
  Pendle               $15,200,000    78    MEDIUM    Yield

💡 INSIGHTS
  • Top opportunity: USDe on Ethena at 12.50% APY
  • Safest protocols: Aave V3, Compound V3, Ondo Finance
  • Best stablecoin yield: DAI on Aave V3 at 5.80% APY
  • Caution: 3 protocols have declining TVL
```

## Supported Chains

Mantle, Ethereum, Arbitrum, Base, Optimism, Polygon, BSC

## Requirements

```
requests>=2.28.0
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

## License

MIT
