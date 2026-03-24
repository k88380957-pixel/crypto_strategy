"""Report generation for the crypto strategy.

This module turns scores and features into a concise, human‑readable
summary.  It lists the top N tokens by score, shows key metrics and
includes the risk assessment.
"""

from __future__ import annotations

from typing import Dict, Any


def generate_report(scores: Dict[str, float], features: Dict[str, Dict[str, Any]], risks: Dict[str, str], top_n: int = 5) -> str:
    """Generate a textual report for the top tokens.

    Args:
        scores: Mapping of token to score.
        features: Mapping of token to feature dictionary.
        risks: Mapping of token to risk label.
        top_n: Number of top tokens to include.

    Returns:
        A multi‑line string summarising the results.
    """
    # Sort tokens by descending score
    sorted_tokens = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    lines = []
    for token, score in sorted_tokens:
        feats = features.get(token, {})
        risk = risks.get(token, "unknown")
        line = (
            f"{token}: score={score:.3f}, risk={risk}, "
            f"7d return={feats.get('return_7d', 0.0):.2%}, "
            f"30d return={feats.get('return_30d', 0.0):.2%}, "
            f"drawdown={feats.get('drawdown', 0.0):.2%}, "
            f"tvl_change_7d={feats.get('tvl_change_7d', 0.0):.2%}, "
            f"sentiment={feats.get('avg_sentiment', 0.0):.2f}"
        )
        lines.append(line)
    return "\n".join(lines)