#!/usr/bin/env python
"""
DeFi Copilot — Your AI-Powered DeFi Research Agent

Scans DeFi protocols across chains, scores risk, analyzes yield opportunities,
and generates actionable research reports. Built for OKX.AI as an ASP.

Usage:
    python copilot.py                      # Full research sweep
    python copilot.py --chain mantle       # Focus on one chain
    python copilot.py --top 10             # Show top 10 opportunities
    python copilot.py --risk-only          # Risk scoring only
    python copilot.py --json               # JSON output
"""

import argparse
import json
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

# ── Configuration ──────────────────────────────────────────────────────────

DEFILLAMA_POOLS = "https://yields.llama.fi/pools"
DEFILLAMA_PROTOCOLS = "https://api.llama.fi/protocols"
DEFILLAMA_TVL = "https://api.llama.fi/v2/historicalChainTvl"

SUPPORTED_CHAINS = ["mantle", "ethereum", "arbitrum", "base", "optimism", "polygon", "bsc"]

# Risk scoring weights
RISK_WEIGHTS = {
    "tvl_size": 20,        # Higher TVL = more battle-tested
    "tvl_trend": 20,       # Growing vs declining
    "audit_coverage": 20,  # Number and quality of audits
    "exploit_history": 20, # Past hacks
    "protocol_age": 20,    # Time since deployment
}

# ── Data Fetching ──────────────────────────────────────────────────────────

def fetch_pools(chain: str = None) -> list:
    """Fetch yield pools from DeFiLlama."""
    try:
        r = requests.get(DEFILLAMA_POOLS, timeout=30)
        r.raise_for_status()
        data = r.json().get("data", [])
    except Exception as e:
        print(f"  ✗ DeFiLlama pools error: {e}", file=sys.stderr)
        return []

    pools = []
    for p in data:
        if chain and p.get("chain", "").lower() != chain.lower():
            continue
        apy = p.get("apy", 0) or 0
        tvl = p.get("tvlUsd", 0) or 0
        if tvl < 10000 or apy <= 0:
            continue
        pools.append({
            "pool": p.get("pool", ""),
            "chain": p.get("chain", ""),
            "project": p.get("project", ""),
            "symbol": p.get("symbol", ""),
            "apy": round(apy, 2),
            "apy_base": round(p.get("apyBase", 0) or 0, 2),
            "apy_reward": round(p.get("apyReward", 0) or 0, 2),
            "tvl": round(tvl, 0),
            "stable": p.get("stablecoin", False),
            "il_risk": p.get("ilRisk", "no"),
            "exposure": p.get("exposure", "single"),
        })

    pools.sort(key=lambda x: -x["tvl"])
    return pools


def fetch_protocols(chain: str = None) -> list:
    """Fetch protocol metadata from DeFiLlama."""
    try:
        r = requests.get(DEFILLAMA_PROTOCOLS, timeout=30)
        r.raise_for_status()
        protocols = r.json()
    except Exception as e:
        print(f"  ✗ DeFiLlama protocols error: {e}", file=sys.stderr)
        return []

    if chain:
        protocols = [p for p in protocols if chain.lower() in [c.lower() for c in p.get("chains", [])]]

    return protocols


# ── Risk Scoring ───────────────────────────────────────────────────────────

def score_tvl(tvl: float) -> int:
    """Score TVL size (0-20). Higher = safer."""
    if tvl >= 1e9:
        return 20
    elif tvl >= 100e6:
        return 17
    elif tvl >= 50e6:
        return 14
    elif tvl >= 10e6:
        return 11
    elif tvl >= 1e6:
        return 8
    elif tvl >= 100e3:
        return 5
    return 2


def score_trend(tvl_change_30d: float) -> int:
    """Score TVL trend (0-20). Growing = better."""
    if tvl_change_30d is None:
        return 12  # Neutral if no data
    if tvl_change_30d > 50:
        return 20
    elif tvl_change_30d > 20:
        return 17
    elif tvl_change_30d > 5:
        return 14
    elif tvl_change_30d > -5:
        return 12
    elif tvl_change_30d > -20:
        return 8
    elif tvl_change_30d > -50:
        return 5
    return 2


def score_audits(audits: int) -> int:
    """Score audit coverage (0-20)."""
    if audits >= 5:
        return 20
    elif audits >= 3:
        return 17
    elif audits >= 2:
        return 14
    elif audits >= 1:
        return 11
    return 5


def score_age(listed_at: str) -> int:
    """Score protocol age (0-20). Older = more battle-tested."""
    if not listed_at:
        return 10
    try:
        listed = datetime.fromisoformat(listed_at.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - listed).days
        if age_days >= 1095:  # 3+ years
            return 20
        elif age_days >= 730:  # 2+ years
            return 17
        elif age_days >= 365:  # 1+ year
            return 14
        elif age_days >= 180:  # 6+ months
            return 11
        elif age_days >= 90:  # 3+ months
            return 8
        return 5
    except Exception:
        return 10


def compute_risk_score(protocol: dict) -> dict:
    """Compute composite risk score for a protocol."""
    tvl = protocol.get("tvl", 0)
    audits = int(protocol.get("audits", "0").replace("+", "")) if protocol.get("audits") else 0
    listed_at = protocol.get("listedAt", "")
    change_30d = protocol.get("tvlChange1M")

    s_tvl = score_tvl(tvl)
    s_trend = score_trend(change_30d)
    s_audit = score_audits(audits)
    s_age = score_age(listed_at)
    s_exploit = 15  # Default (no exploit data available from DeFiLlama)

    total = s_tvl + s_trend + s_audit + s_exploit + s_age

    if total >= 80:
        label = "LOW"
    elif total >= 60:
        label = "MEDIUM"
    elif total >= 40:
        label = "ELEVATED"
    else:
        label = "HIGH"

    return {
        "name": protocol.get("name", "Unknown"),
        "chain": ", ".join(protocol.get("chains", [])),
        "tvl": round(tvl, 0),
        "category": protocol.get("category", "Unknown"),
        "score": total,
        "label": label,
        "breakdown": {
            "tvl_size": s_tvl,
            "tvl_trend": s_trend,
            "audit_coverage": s_audit,
            "exploit_history": s_exploit,
            "protocol_age": s_age,
        },
        "audits": audits,
        "listed_at": listed_at,
        "url": protocol.get("url", ""),
    }


# ── Yield Analysis ─────────────────────────────────────────────────────────

def rank_opportunities(pools: list, top_n: int = 10) -> list:
    """Rank yield opportunities by a composite score (APY × safety)."""
    scored = []
    for p in pools:
        # Penalize high APY (often unsustainable)
        apy_score = min(p["apy"], 100)  # Cap at 100%
        tvl_score = min(p["tvl"] / 1e6, 100)  # Normalize to millions
        stable_bonus = 1.2 if p["stable"] else 1.0
        il_penalty = 0.7 if p["il_risk"] == "yes" else 1.0

        composite = (apy_score * 0.4 + tvl_score * 0.3) * stable_bonus * il_penalty
        p["composite_score"] = round(composite, 2)
        scored.append(p)

    scored.sort(key=lambda x: -x["composite_score"])
    return scored[:top_n]


# ── Report Generation ──────────────────────────────────────────────────────

def generate_report(chain: str, pools: list, protocols: list, top_n: int = 10) -> dict:
    """Generate a comprehensive DeFi research report."""
    # Risk scoring
    risk_scores = []
    for p in protocols[:50]:  # Top 50 by TVL
        score = compute_risk_score(p)
        risk_scores.append(score)
    risk_scores.sort(key=lambda x: -x["score"])

    # Yield ranking
    top_yields = rank_opportunities(pools, top_n)

    # Chain stats
    total_tvl = sum(p.get("tvl", 0) for p in pools)
    avg_apy = sum(p["apy"] for p in pools) / len(pools) if pools else 0
    stable_pools = [p for p in pools if p["stable"]]
    stable_pct = len(stable_pools) / len(pools) * 100 if pools else 0

    # Find top protocol
    top_protocol = risk_scores[0] if risk_scores else None

    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "chain": chain or "all",
        "summary": {
            "total_pools": len(pools),
            "total_tvl": round(total_tvl, 0),
            "avg_apy": round(avg_apy, 2),
            "stable_pool_pct": round(stable_pct, 1),
            "protocols_analyzed": len(risk_scores),
        },
        "top_yields": top_yields,
        "risk_scores": risk_scores[:15],
        "insights": generate_insights(pools, risk_scores, top_yields),
    }


def generate_insights(pools: list, risk_scores: list, top_yields: list) -> list:
    """Generate actionable insights from the data."""
    insights = []

    # Best risk-adjusted yield
    if top_yields:
        best = top_yields[0]
        insights.append(f"Top opportunity: {best['symbol']} on {best['project']} at {best['apy']}% APY (TVL: ${best['tvl']:,.0f})")

    # Safest protocols
    low_risk = [r for r in risk_scores if r["label"] == "LOW"]
    if low_risk:
        insights.append(f"Safest protocols: {', '.join(r['name'] for r in low_risk[:3])}")

    # Highest APY stablecoin pools
    stable_high = [p for p in pools if p["stable"] and p["apy"] > 5]
    if stable_high:
        best_stable = max(stable_high, key=lambda x: x["apy"])
        insights.append(f"Best stablecoin yield: {best_stable['symbol']} on {best_stable['project']} at {best_stable['apy']}% APY")

    # Protocols with declining TVL
    declining = [r for r in risk_scores if r["breakdown"]["tvl_trend"] <= 5]
    if declining:
        insights.append(f"Caution: {len(declining)} protocols have declining TVL (potential red flag)")

    return insights


def format_report(report: dict) -> str:
    """Format report for terminal output."""
    lines = []
    lines.append("=" * 65)
    lines.append("  DEFI COPILOT — RESEARCH REPORT")
    lines.append(f"  {report['timestamp']} | Chain: {report['chain'].upper()}")
    lines.append("=" * 65)

    s = report["summary"]
    lines.append(f"\n📊 ECOSYSTEM OVERVIEW")
    lines.append(f"  {'─'*40}")
    lines.append(f"  Active Pools:     {s['total_pools']}")
    lines.append(f"  Total TVL:        ${s['total_tvl']:,.0f}")
    lines.append(f"  Average APY:      {s['avg_apy']:.2f}%")
    lines.append(f"  Stablecoin Pools: {s['stable_pool_pct']:.1f}%")

    # Top yields
    lines.append(f"\n🏆 TOP YIELD OPPORTUNITIES")
    lines.append(f"  {'─'*65}")
    lines.append(f"  {'#':<4} {'Symbol':<20} {'Protocol':<18} {'APY':>8} {'TVL':>14} {'Risk'}")
    lines.append(f"  {'─'*4} {'─'*20} {'─'*18} {'─'*8} {'─'*14} {'─'*6}")
    for i, p in enumerate(report["top_yields"], 1):
        stable = "🟢" if p["stable"] else "  "
        lines.append(f"  {i:<4} {p['symbol']:<20} {p['project']:<18} {p['apy']:>7.2f}% ${p['tvl']:>12,.0f} {stable}")

    # Risk scores
    lines.append(f"\n🛡️ PROTOCOL RISK SCORES")
    lines.append(f"  {'─'*65}")
    lines.append(f"  {'Protocol':<25} {'TVL':>12} {'Score':>6} {'Label':>10} {'Category'}")
    lines.append(f"  {'─'*25} {'─'*12} {'─'*6} {'─'*10} {'─'*15}")
    for r in report["risk_scores"][:10]:
        lines.append(f"  {r['name']:<25} ${r['tvl']:>10,.0f} {r['score']:>5} {r['label']:>10} {r['category']:<15}")

    # Insights
    lines.append(f"\n💡 INSIGHTS")
    lines.append(f"  {'─'*40}")
    for insight in report["insights"]:
        lines.append(f"  • {insight}")

    lines.append(f"\n{'='*65}")
    return "\n".join(lines)


def generate_x_post(report: dict) -> str:
    """Generate an X post from the report."""
    chain = report["chain"].upper()
    s = report["summary"]
    top = report["top_yields"][:3] if report["top_yields"] else []
    low_risk = [r for r in report["risk_scores"] if r["label"] == "LOW"][:3]

    lines = [f"🔍 {chain} DeFi Research — Live Scan\n"]

    if top:
        lines.append("📊 Top yield opportunities:\n")
        for i, p in enumerate(top, 1):
            lines.append(f"{i}. {p['symbol']} ({p['project']})")
            lines.append(f"   APY: {p['apy']}% | TVL: ${p['tvl']:,.0f}\n")

    lines.append(f"📈 Total TVL: ${s['total_tvl']:,.0f} | {s['total_pools']} pools analyzed")

    if low_risk:
        lines.append(f"\n🛡️ Safest protocols: {', '.join(r['name'] for r in low_risk)}")

    lines.append(f"\n#DeFi #OKXAI #FinanceCopilot #OnchainResearch")

    return "\n".join(lines)


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="DeFi Copilot — AI-Powered DeFi Research Agent")
    p.add_argument("--chain", default=None, help=f"Focus chain ({', '.join(SUPPORTED_CHAINS)})")
    p.add_argument("--top", type=int, default=10, help="Number of top opportunities to show")
    p.add_argument("--risk-only", action="store_true", help="Only show risk scores")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--x-post", action="store_true", help="Generate X post")
    args = p.parse_args()

    print("🤖 DeFi Copilot — AI-Powered Research Agent")
    print(f"   Chain: {args.chain or 'All supported chains'}\n")

    # Fetch data
    print("📊 Fetching live data from DeFiLlama...")
    pools = fetch_pools(args.chain)
    protocols = fetch_protocols(args.chain)
    print(f"   Found {len(pools)} pools, {len(protocols)} protocols\n")

    if not pools:
        print("  ✗ No data found")
        sys.exit(1)

    # Generate report
    report = generate_report(args.chain, pools, protocols, args.top)

    if args.json:
        print(json.dumps(report, indent=2))
    elif args.x_post:
        print(generate_x_post(report))
    elif args.risk_only:
        for r in report["risk_scores"][:args.top]:
            print(f"  {r['name']:<25} Score: {r['score']:>3} ({r['label']})")
    else:
        print(format_report(report))

    # Save report
    report_path = "latest_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Report saved to: {report_path}")


if __name__ == "__main__":
    main()
