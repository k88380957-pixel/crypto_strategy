"""Scoring logic for the crypto strategy.

This module normalises features across all tokens and combines them
according to user‑defined weights.  Lower drawdowns and volatilities
improve the score (i.e. they are inversely weighted).  All other
metrics are scored directly.
"""

from __future__ import annotations

from typing import Dict, Any


def _normalise(value: float, min_val: float, max_val: float) -> float:
    """Scale a value to the [0, 1] range given minimum and maximum bounds.

    If ``min_val`` equals ``max_val``, returns 0.0 to avoid division by
    zero.
    """
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)


def compute_scores(tokens_features: Dict[str, Dict[str, Any]], weights: Dict[str, float]) -> Dict[str, float]:
    """Compute a composite score for each token.

    Args:
        tokens_features: A mapping from token to its feature dictionary.
        weights: A mapping from feature name to weight.  Features absent
            from ``weights`` are ignored.

    Returns:
        A mapping from token to its normalised, weighted score.
    """
    # Collect all values per feature to compute min/max
    feature_values: Dict[str, list] = {}
    for feats in tokens_features.values():
        for k, v in feats.items():
            feature_values.setdefault(k, []).append(v)
    feature_min_max: Dict[str, tuple] = {}
    for k, vals in feature_values.items():
        feature_min_max[k] = (min(vals), max(vals))
    scores: Dict[str, float] = {}
    for token, feats in tokens_features.items():
        score = 0.0
        for feat_name, weight in weights.items():
            if weight == 0:
                continue
            value = feats.get(feat_name, 0.0)
            min_val, max_val = feature_min_max.get(feat_name, (0.0, 1.0))
            # Normalise
            norm = _normalise(value, min_val, max_val)
            # Invert metrics where lower is better
            if feat_name in {"drawdown", "volatility"}:
                norm = 1.0 - norm
            score += weight * norm
        scores[token] = score
    return scores