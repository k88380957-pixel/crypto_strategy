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

import os
import requests


def send_telegram_message(message: str, chat_id: str, bot_token: str) -> None:
    """Send a message to a Telegram chat.

    Args:
        message: The text to send.
        chat_id: The Telegram chat identifier (can be a channel ID or user ID).
        bot_token: The Telegram bot token.

    This helper wraps the Telegram Bot API. It will silently
    ignore network errors to avoid raising exceptions during the
    scheduled run. To troubleshoot, inspect the workflow logs.
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
    except Exception:
        # Log but do not raise; GitHub Action will capture stderr
        import sys
        print("Failed to send Telegram message", file=sys.stderr)


def generate_gemini_summary(text: str, api_key: str) -> str:
    """Generate a concise summary of the given text using Gemini API.

    Args:
        text: The input text to summarise.
        api_key: The Gemini API key.

    Returns:
        A summary string returned by the Gemini API. If the request
        fails for any reason, the original text is returned.
    """
    try:
        # Endpoint for Google generative language API (Gemini). This
        # endpoint may change over time; refer to official docs. The
        # model name "gemini-pro" provides general purpose summarisation.
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"
        params = {"key": api_key}
        payload = {
            "prompt": {"text": text},
            "maxTokens": 256,
            "temperature": 0.5,
        }
        resp = requests.post(url, params=params, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        # Extract the first candidate's output
        candidates = data.get("candidates", [])
        if candidates:
            output = candidates[0].get("output", "").strip()
            return output if output else text
    except Exception:
        import sys
        print("Failed to summarise via Gemini", file=sys.stderr)
    return text


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
    # Generate the textual report
    report = generate_report(scores, token_features, risks, top_n=5)

    # Determine if summarisation via Gemini is configured
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    message = report
    if gemini_api_key:
        message = generate_gemini_summary(report, gemini_api_key)

    # Print the report (for logs)
    print(message)

    # Send to Telegram if credentials are available
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if telegram_token and telegram_chat_id:
        send_telegram_message(message, telegram_chat_id, telegram_token)

    return 0


if __name__ == "__main__":
    sys.exit(main())