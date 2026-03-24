"""Global configuration for the crypto strategy framework.

This file defines the list of tokens to analyse, news feeds to crawl,
weightings for the composite score and API endpoints.  Environment
variables are read for optional third party services that require
authentication (e.g. CoinMetrics, Santiment, Whale Alert).
"""

import os

# List of token IDs (as recognised by CoinGecko and DeFiLlama) to analyse.
TOKENS = [
    "bitcoin",
    "ethereum",
    "tether",
    "tron",
    "binancecoin",
    "solana",
    "cardano",
    "dogecoin",
]

# RSS feeds from which to pull news headlines and summaries.
RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
    "https://cointelegraph.com/rss",
    "https://theblock.co/rss",
]

# Weightings for the composite score.  Keys correspond to feature names.
WEIGHTS = {
    "return_7d": 0.15,
    "return_30d": 0.10,
    "tvl_change_7d": 0.15,
    "tvl_change_30d": 0.15,
    "drawdown": 0.15,
    "volatility": 0.10,
    "active_addresses": 0.10,
    "whale_flow": 0.10,
    "exchange_net_flow": 0.05,
    "mentions": 0.05,
    "avg_sentiment": 0.05,
}

# Number of days of historical data to fetch for prices and on chain metrics.
LOOKBACK_DAYS = 30

# Base API endpoints.
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
DEFILLAMA_API_BASE = "https://api.llama.fi"

# Read API keys from environment variables.  These keys are optional – if not
# provided, the corresponding data source is skipped.
CM_API_KEY = os.getenv("CM_API_KEY")  # CoinMetrics API key
SAN_API_KEY = os.getenv("SAN_API_KEY")  # Santiment API key
WHALE_ALERT_API_KEY = os.getenv("WHALE_ALERT_API_KEY")  # Whale Alert API key
