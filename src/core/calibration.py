"""
Calibration — Sincronização de thresholds adaptativos.

Aceita tanto lista de floats (scores pré-processados) quanto
lista de dicionários de métricas brutas (auto-processados via compute_score).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Union

from core.eeg_adapter import AdaptiveThresholds, compute_score


@dataclass
class CalibrationResult:
    """
    Hybrid calibration result supporting both local and remote APIs.

    Remote API: result.baseline_mean, result.baseline_std, result.low, result.high
    Local API:  result.thresholds.low, result.thresholds.high
    """

    baseline_mean: float
    baseline_std: float
    low: float
    high: float
    thresholds: AdaptiveThresholds = field(default=None)

    def __post_init__(self):
        if self.thresholds is None:
            self.thresholds = AdaptiveThresholds(low=self.low, high=self.high)


def calibrate_thresholds(
    data: Union[List[float], List[Dict[str, float]]],
    n_std: float = 1.0,
) -> CalibrationResult:
    """
    Compute adaptive thresholds from baseline data.

    Accepts:
      - List[float]: pre-computed scores
      - List[Dict]: raw EEG feature windows (auto-processed via compute_score)

    Thresholds:
      low  = mean + 1 * n_std * std   (transition boundary)
      high = mean + 2 * n_std * std   (confirmation boundary)
    """
    if not data:
        raise ValueError("data must not be empty")

    # Auto-detect and convert to scores
    if isinstance(data[0], dict):
        scores = [compute_score(w) for w in data]
    else:
        scores = [float(s) for s in data]

    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std = math.sqrt(variance)

    low = mean + n_std * std
    high = mean + 2.0 * n_std * std

    return CalibrationResult(
        baseline_mean=mean,
        baseline_std=std,
        low=low,
        high=high,
    )


def state_from_score(
    score: float,
    low_or_thresholds=None,
    high: float = None,
) -> int:
    """
    Map a scalar score to a discrete intent state.

    Supports two calling conventions:
      state_from_score(score, low, high)          — remote API
      state_from_score(score, thresholds_obj)      — local API

    Returns:
       1   confirmed intent   (score >= high)
       0   ambiguous          (low <= score < high)
      -1   disconnection/idle (score < low)
    """
    if isinstance(low_or_thresholds, AdaptiveThresholds):
        low_val = low_or_thresholds.low
        high_val = low_or_thresholds.high
    elif high is not None:
        low_val = float(low_or_thresholds)
        high_val = float(high)
    else:
        raise TypeError(
            "state_from_score requires either (score, low, high) or "
            "(score, AdaptiveThresholds)"
        )

    if score >= high_val:
        return 1
    if score >= low_val:
        return 0
    return -1
