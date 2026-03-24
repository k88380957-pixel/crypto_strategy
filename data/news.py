"""News fetching and sentiment analysis.

This module fetches news articles from RSS feeds and analyses their
sentiment using the VaderSentiment library.  It also associates
mentions with the tokens defined in the configuration.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable, Dict, Any, List

import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Initialise the sentiment analyser once to avoid overhead.
_analyser = SentimentIntensityAnalyzer()


def fetch_news(rss_feeds: Iterable[str]) -> List[Dict[str, Any]]:
    """Fetch news items from the provided RSS feeds.

    Args:
        rss_feeds: An iterable of RSS feed URLs.

    Returns:
        A list of dictionaries containing the title, summary and
        published date for each news item.
    """
    items: List[Dict[str, Any]] = []
    for feed_url in rss_feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in getattr(feed, "entries", []):
                items.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", entry.get("description", "")),
                    "published": entry.get("published", ""),
                })
        except Exception:
            # Silently ignore failing feeds
            continue
    return items


def analyse_sentiment(text: str) -> float:
    """Compute the compound sentiment score of the provided text.

    A positive value indicates positive sentiment, a negative value
    indicates negative sentiment and values near zero indicate neutral
    sentiment.

    Args:
        text: The input text.

    Returns:
        A float between -1 and 1 representing the compound sentiment.
    """
    if not text:
        return 0.0
    score = _analyser.polarity_scores(text)
    return score.get("compound", 0.0)


def summarise_news(news_items: Iterable[Dict[str, Any]], tokens: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    """Aggregate sentiment and mention counts for each token from news items.

    The function tokenises the text by searching for exact occurrences of
    the token name (case insensitive).  For each occurrence, it records
    the sentiment score of the article.  The final result contains the
    number of mentions and the average sentiment per token.

    Args:
        news_items: A list of news items as returned by ``fetch_news``.
        tokens: A list of token identifiers/names to search for.

    Returns:
        A mapping from token to a dictionary with keys ``mentions`` and
        ``avg_sentiment``.
    """
    token_sentiments: Dict[str, List[float]] = defaultdict(list)
    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        sentiment_score = analyse_sentiment(text)
        for token in tokens:
            pattern = rf"\b{re.escape(token)}\b"
            if re.search(pattern, text, re.IGNORECASE):
                token_sentiments[token].append(sentiment_score)
    summary: Dict[str, Dict[str, Any]] = {}
    for token in tokens:
        scores = token_sentiments.get(token, [])
        if scores:
            avg = sum(scores) / len(scores)
            summary[token] = {
                "mentions": len(scores),
                "avg_sentiment": avg,
            }
        else:
            summary[token] = {
                "mentions": 0,
                "avg_sentiment": 0.0,
            }
    return summary
