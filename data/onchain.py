"""Optional on‑chain metrics for the crypto strategy.

This module fetches active address counts, whale transactions and
exchange net flows when API keys are provided.  Each function returns
``None`` if the corresponding API key is missing or if the request
fails.  Users can supply API keys via environment variables (see
``config.py``).
"""

from __future__ import annotations

import datetime
import requests
from typing import Optional, Any

from .. import config


def get_active_addresses(asset: str, days: int = 30) -> Optional[Any]:
    """Fetch daily active address counts for the specified asset.

    This function uses the CoinMetrics API (v4).  An API key must be
    provided via the ``CM_API_KEY`` environment variable.  If no key is
    supplied, the function returns ``None``.

    Args:
        asset: The asset symbol recognised by CoinMetrics (e.g. ``btc``).
        days: Number of days of history to fetch.

    Returns:
        The JSON data structure returned by CoinMetrics or ``None``.
    """
    if not config.CM_API_KEY:
        return None
    base_url = "https://api.coinmetrics.io/v4"
    end_date = datetime.datetime.utcnow().date()
    start_date = end_date - datetime.timedelta(days=days)
    url = f"{base_url}/timeseries/asset-metrics"
    params = {
        "assets": asset,
        "metrics": "AdrActCnt",
        "frequency": "1d",
        "start_time": start_date.isoformat(),
        "end_time": end_date.isoformat(),
        "api_key": config.CM_API_KEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        return resp.json().get("data")
    except Exception:
        return None


def get_whale_transactions(symbol: str, min_value_usd: int = 500_000, days: int = 1) -> Optional[Any]:
    """Retrieve recent large transactions for the given symbol via Whale Alert.

    Whale Alert provides a REST API for monitoring significant transfers.
    An API key is required and must be supplied via ``WHALE_ALERT_API_KEY``.

    Args:
        symbol: The currency symbol (e.g. ``btc``, ``eth``, ``trx``).
        min_value_usd: Minimum USD value of transfers to return.
        days: Number of days to look back.

    Returns:
        Parsed JSON from Whale Alert or ``None``.
    """
    if not config.WHALE_ALERT_API_KEY:
        return None
    end_ts = int(datetime.datetime.utcnow().timestamp())
    start_ts = end_ts - days * 86400
    url = "https://api.whale-alert.io/v1/transactions"
    params = {
        "api_key": config.WHALE_ALERT_API_KEY,
        "symbol": symbol,
        "min_value": min_value_usd,
        "start": start_ts,
        "end": end_ts,
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        return resp.json()
    except Exception:
        return None


def get_exchange_net_flow(asset: str, days: int = 7) -> Optional[Any]:
    """Fetch exchange net flow timeseries for the specified asset.

    This function uses the Santiment GraphQL API.  A valid API key must
    be provided via ``SAN_API_KEY``.  Without a key, the function
    returns ``None``.

    Args:
        asset: The slug recognised by Santiment (e.g. ``bitcoin``).
        days: Number of days of history to fetch.

    Returns:
        A parsed JSON structure from Santiment or ``None``.
    """
    if not config.SAN_API_KEY:
        return None
    url = "https://api.santiment.net/graphql"
    query = """
    query GetExchangeNetflow($slug: String!, $from: DateTime!, $to: DateTime!, $interval: String!) {
      getMetric(metric: "exchange_balance") {
        timeseriesData(
          slug: $slug,
          from: $from,
          to: $to,
          interval: $interval
        ) {
          datetime
          value
        }
      }
    }
    """
    end_ts = datetime.datetime.utcnow()
    start_ts = end_ts - datetime.timedelta(days=days)
    variables = {
        "slug": asset,
        "from": start_ts.isoformat() + "Z",
        "to": end_ts.isoformat() + "Z",
        "interval": "1d",
    }
    try:
        resp = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers={"Authorization": f"Apikey {config.SAN_API_KEY}"},
            timeout=30,
        )
        return resp.json()
    except Exception:
        return None