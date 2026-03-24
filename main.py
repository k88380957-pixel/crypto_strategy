"""Entry point for the crypto strategy pipeline.

Running this script will fetch news, price history and TVL data for the
configured tokens, compute features, score each token, assess risk and
output a ranked report.  Optional on‑chain metrics (active
addresses, whale flows, exchange flows) are fetched only when
corresponding API keys are provided.
"""

from __future__ import annotations

import sys
from typing import Dict, Any

from config import TOKENS, RSS_FEEDS, WEIGHTS, LOOKBACK_DAYS
from data.news import fetch_news, summarise_news
from data.defillama import get_tvl_stats
from data.coingecko import get_price_history
from data.onchain import get_active_addresses, get_whale_transactions, get_exchange_net_flow
from analysis.features import compute_price_features, compute_tvl_features, compute_news_features
from analysis.scoring import compute_scores
from analysis.risk import assess_risk
from analysis.report import generate_report


def main() -> int:
    # Fetch news and build sentiment summary
    news_items = fetch_news(RSS_FEEDS)
    news_summary = summarise_news(news_items, TOKENS)
    # Collect features per token
    token_features: Dict[str, Dict[str, Any]] = {}
    for token in TOKENS:
        # Price features
        price_df = get_price_history(token, days=LOOKBACK_DAYS)
        price_feats = compute_price_features(price_df)
        # TVL features
        tvl_stats = get_tvl_stats(token)
        tvl_feats = compute_tvl_features(tvl_stats)
        # News features
        token_news_summary = news_summary.get(token, {"mentions": 0, "avg_sentiment": 0.0})
        news_feats = compute_news_features(token_news_summary)
        # On‑chain features (optional)
        # Active addresses
        # Not used directly in scoring but could be added to token_features for risk or further analysis
        active_addresses_data = get_active_addresses(token)
        # Whale flows
        whale_data = get_whale_transactions(token)
        # Exchange flows
        exchange_flow_data = get_exchange_net_flow(token)
        # Combine features
        feats = {}
        feats.update(price_feats)
        feats.update(tvl_feats)
        feats.update({
            "mentions": news_feats["mentions"],
            "avg_sentiment": news_feats["avg_sentiment"],
        })
        # Additional features from optional metrics could be added here
        token_features[token] = feats
    # Compute composite scores
    scores = compute_scores(token_features, WEIGHTS)
    # Assess risk
    risks = {token: assess_risk(feats) for token, feats in token_features.items()}
    # Generate and print report
    report = generate_report(scores, token_features, risks, top_n=5)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
