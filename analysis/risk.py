"""Risk assessment for the crypto strategy.

This module provides a simple heuristic to classify tokens into low,
medium or high risk categories based on volatility, drawdown and TVL
declines.  The risk score is additive: higher volatility, larger
drawdowns and declining TVL increase the risk rating.
"""

from __future__ import annotations

from typing import Dict


def assess_risk(features: Dict[str, float]) -> str:
    """Assign a risk label (low/medium/high) based on numeric features.

    Args:
        features: A mapping of feature names to numeric values.  The
            function looks at ``volatility``, ``drawdown`` and
            ``tvl_change_30d``.

    Returns:
        A string ``low``, ``medium`` or ``high`` denoting the risk
        level.
    """
    risk_score = 0.0
    vol = abs(features.get("volatility", 0.0))
    risk_score += vol
    drawdown = abs(features.get("drawdown", 0.0))
    risk_score += drawdown
    tvl_change = features.get("tvl_change_30d", 0.0)
    # Declining TVL contributes to risk
    if tvl_change < 0:
        risk_score += abs(tvl_change)
    if risk_score < 0.3:
        return "low"
    elif risk_score < 0.6:
        return "medium"
    else:
        return "high"