from dataclasses import dataclass
from typing import List, Dict
import statistics
from .eeg_adapter import AdaptiveThresholds

@dataclass
class CalibrationResult:
    thresholds: AdaptiveThresholds
    baseline_mean: float
    baseline_std: float

def calibrate_thresholds(baseline_data: List[float]) -> CalibrationResult:
    """
    Estipula low/high automaticamente com base na sessão real (mean e standard dev).
    """
    if not baseline_data:
        return CalibrationResult(AdaptiveThresholds(0.0, 1.0), 0.5, 0.1)
    
    mean = statistics.mean(baseline_data)
    std = statistics.pstdev(baseline_data) if len(baseline_data) > 1 else 0.1
    
    thresholds = AdaptiveThresholds(
        low=mean - std,
        high=mean + std
    )
    return CalibrationResult(thresholds, mean, std)

def state_from_score(score: float, thresholds: AdaptiveThresholds) -> int:
    """
    Recupera um estado categórico dado um threshold.
    """
    if score >= thresholds.high:
        return 1
    elif score <= thresholds.low:
        return -1
    return 0
