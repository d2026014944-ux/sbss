from dataclasses import dataclass
from typing import Dict

@dataclass
class AdaptiveThresholds:
    low: float = 0.0
    high: float = 1.0

def compute_score(metrics: Dict[str, float]) -> float:
    """Calcula um score simples para o MVP usando métricas como Alpha/Beta."""
    alpha = metrics.get("alpha", 0.0)
    beta = metrics.get("beta", 1.0)
    return alpha / (beta + 1e-5)

def adaptive_state(score: float, thresholds: AdaptiveThresholds) -> int:
    """Classifica o input baseado nos limites adaptativos."""
    if score > thresholds.high:
        return 1
    elif score < thresholds.low:
        return -1
    return 0
