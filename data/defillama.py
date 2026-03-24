"""Interface to the DeFiLlama API.

This module fetches TVL and protocol statistics from DeFiLlama.  It uses
simple ``requests`` calls and returns parsed JSON structures.  See
https://defillama.com/ for more information.
"""

from __future__ import annotations

import datetime
import requests
from typing import Dict, Any, Optional

from .. import config


def _get_protocol_data(protocol: str) -> Optional[Dict[str, Any]]:
    """Retrieve raw protocol data from DeFiLlama.

    Args:
        protocol: The protocol slug, e.g. ``ethereum`` or ``uniswap``.

    Returns:
        Parsed JSON data if available, otherwise ``None``.
    """
    url = f"{config.DEFILLAMA_API_BASE}/protocol/{protocol}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def get_tvl_stats(protocol: str) -> Dict[str, float]:
    """Compute current TVL and short‑term changes for a protocol.

    The function fetches the protocol's TVL history and calculates the
    7‑day and 30‑day percentage change relative to the current value.

    Args:
        protocol: The protocol slug to query.

    Returns:
        A dictionary with keys ``tvl``, ``tvl_change_7d`` and ``tvl_change_30d``.
        Empty if no data could be retrieved.
    """
    data = _get_protocol_data(protocol)
    if not data:
        return {}
    tvl_list = data.get("tvl", [])
    if not tvl_list:
        return {}
    # Sort by timestamp
    sorted_tvl = sorted(tvl_list, key=lambda x: x["date"])
    # Current TVL is the last entry's value
    current = sorted_tvl[-1]["totalLiquidityUSD"]
    now_ts = datetime.datetime.now().timestamp()
    ts_7d = now_ts - 7 * 24 * 3600
    ts_30d = now_ts - 30 * 24 * 3600
    tvl_7d = current
    tvl_30d = current
    # Find the earliest TVL not older than 7/30 days
    for item in reversed(sorted_tvl):
        if item["date"] >= ts_7d:
            tvl_7d = item["totalLiquidityUSD"]
            break
    for item in reversed(sorted_tvl):
        if item["date"] >= ts_30d:
            tvl_30d = item["totalLiquidityUSD"]
            break
    change_7d = (current - tvl_7d) / tvl_7d if tvl_7d else 0
    change_30d = (current - tvl_30d) / tvl_30d if tvl_30d else 0
    return {
        "tvl": current,
        "tvl_change_7d": change_7d,
        "tvl_change_30d": change_30d,
    }