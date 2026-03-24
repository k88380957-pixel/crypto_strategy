"""Interface to the CoinGecko API.

This module wraps a few endpoints of the public CoinGecko API to fetch
price history and current market data for tokens.  All requests are
unauthenticated and subject to CoinGecko rate limits.
"""

from __future__ import annotations

import requests
import pandas as pd
from typing import Dict, Any

from .. import config


def get_price_history(token: str, days: int = 30) -> pd.DataFrame:
    """Retrieve historical price data for a token.

    Args:
        token: The CoinGecko ID of the token (e.g. ``bitcoin``).
        days: Number of days of history to fetch.

    Returns:
        A DataFrame with columns ``timestamp`` (datetime) and ``price`` (float).
        If the request fails, returns an empty DataFrame.
    """
    url = f"{config.COINGECKO_API_BASE}/coins/{token}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        prices = data.get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        if df.empty:
            return df
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception:
        return pd.DataFrame(columns=["timestamp", "price"])


def get_current_market_data(token: str) -> Dict[str, Any]:
    """Fetch current market data for a token.

    Args:
        token: The token ID.

    Returns:
        A dictionary containing current price, market cap and other fields
        returned by the API, or an empty dict if the request fails.
    """
    url = f"{config.COINGECKO_API_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": token,
        "sparkline": "false",
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        if data:
            return data[0]
        return {}
    except Exception:
        return {}