"""Feature engineering for the crypto strategy.

This module provides functions to compute derived metrics from price
history, TVL statistics and news sentiment.  It aggregates these
metrics into dictionaries that can be passed to the scoring function.
"""

from __future__ import annotations

import pandas as pd
from typing import Dict, Any


def compute_price_features(price_df: pd.DataFrame) -> Dict[str, float]:
    """Derive price‑based metrics from historical prices.

    Metrics include short‑term returns, volatility and maximum drawdown.

    Args:
        price_df: A DataFrame with columns ``timestamp`` and ``price``.

    Returns:
        A dictionary with keys:
        ``return_7d`` – percentage change between the latest price and
        the price 7 entries ago (approx. one week for daily data);
        ``return_30d`` – change relative to the first entry;
        ``volatility`` – standard deviation of daily returns;
        ``drawdown`` – maximum drawdown (as a negative fraction).
    """
    if price_df is None or price_df.empty:
        return {
            "return_7d": 0.0,
            "return_30d": 0.0,
            "volatility": 0.0,
            "drawdown": 0.0,
        }
    price_df = price_df.sort_values("timestamp").reset_index(drop=True)
    current_price = price_df["price"].iloc[-1]
    idx_7d = max(0, len(price_df) - 7)
    price_7d = price_df["price"].iloc[idx_7d]
    price_30d = price_df["price"].iloc[0]
    return_7d = (current_price - price_7d) / price_7d if price_7d else 0.0
    return_30d = (current_price - price_30d) / price_30d if price_30d else 0.0
    # Compute daily returns for volatility
    price_df["returns"] = price_df["price"].pct_change().fillna(0.0)
    volatility = price_df["returns"].std() if len(price_df) > 1 else 0.0
    # Drawdown: difference between current price and rolling max, divided by rolling max
    cummax = price_df["price"].cummax()
    drawdowns = (price_df["price"] - cummax) / cummax
    max_drawdown = drawdowns.min()  # negative value
    return {
        "return_7d": return_7d,
        "return_30d": return_30d,
        "volatility": volatility,
        "drawdown": max_drawdown,
    }


def compute_tvl_features(tvl_stats: Dict[str, float]) -> Dict[str, float]:
    """Extract TVL change metrics from raw stats.

    Args:
        tvl_stats: A dictionary returned by ``data.defillama.get_tvl_stats``.

    Returns:
        A dictionary with keys ``tvl_change_7d`` and ``tvl_change_30d``.
    """
    if not tvl_stats:
        return {
            "tvl_change_7d": 0.0,
            "tvl_change_30d": 0.0,
        }
    return {
        "tvl_change_7d": tvl_stats.get("tvl_change_7d", 0.0),
        "tvl_change_30d": tvl_stats.get("tvl_change_30d", 0.0),
    }


def compute_news_features(news_summary: Dict[str, Any]) -> Dict[str, float]:
    """Produce news‑related features from sentiment summary.

    Args:
        news_summary: A dictionary with keys ``mentions`` and
            ``avg_sentiment`` for a given token.

    Returns:
        A dictionary with the same keys but cast to floats.
    """
    return {
        "mentions": float(news_summary.get("mentions", 0)),
        "avg_sentiment": float(news_summary.get("avg_sentiment", 0.0)),
    }
