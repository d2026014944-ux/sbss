"""
EEG Adapter — Tradutor de frequências biológicas para vetores de ressonância.

Suporta múltiplos domínios de entrada via auto-detecção por chaves:
  - Neurosity (focus, calm, gamma) → modelo ponderado
  - Legacy (alpha, beta) → modelo de razão
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class AdaptiveThresholds:
    """Adaptive threshold boundaries for intent classification."""

    low: float = 0.0
    high: float = 1.0


def compute_score(features: Dict[str, float]) -> float:
    """
    Compute a scalar activation score from EEG-derived features.

    Auto-detects input domain by dictionary keys:

    Neurosity domain (focus/gamma/calm):
      focus  -> 0.5  (primary intent signal)
      gamma  -> 0.3  (cognitive engagement)
      calm   -> 0.2  (inverse: low calm = high arousal)

    Legacy domain (alpha/beta):
      score = alpha / (beta + 1e-5)

    Returns a value in [0, 1].
    """
    # Neurosity domain detection
    if "focus" in features or "gamma" in features or "calm" in features:
        focus = float(features.get("focus", 0.0))
        gamma = float(features.get("gamma", 0.0))
        calm = float(features.get("calm", 0.0))
        score = focus * 0.5 + gamma * 0.3 + (1.0 - calm) * 0.2
        return max(0.0, min(1.0, score))

    # Legacy domain detection
    if "alpha" in features or "beta" in features:
        alpha = float(features.get("alpha", 0.0))
        beta = float(features.get("beta", 1.0))
        score = alpha / (beta + 1e-5)
        return max(0.0, min(1.0, score))

    # Fallback: average of all values
    if features:
        vals = [float(v) for v in features.values()]
        return max(0.0, min(1.0, sum(vals) / len(vals)))

    return 0.0


def adaptive_state(score: float, thresholds: AdaptiveThresholds) -> int:
    """Classify input based on adaptive threshold boundaries."""
    if score >= thresholds.high:
        return 1
    elif score <= thresholds.low:
        return -1
    return 0
