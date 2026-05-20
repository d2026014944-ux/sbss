"""
TRIBE Adapter — Tradução de intenção ressonante para ação externa.

Mapeia um vetor contínuo de intenção em comandos de alto nível para o
sistema TRIBE, com compatibilidade entre as APIs remota e local.
"""

from typing import Dict, List


def to_tribe_command(intent_vector: List[float]) -> Dict[str, object]:
    """
    Translate a continuous intent vector into a high-level TRIBE command.

    The mean energy of the vector determines the command:
      >= 0.65  -> CONFIRM_INTENT  (strong, sustained activation)
      >= 0.40  -> TRANSITION      (rising / ambiguous activation)
      < 0.40   -> IDLE            (resting / no intent detected)

    Returns a dict with both standard and legacy fields for compatibility.
    """
    if not intent_vector:
        return {
            "command": "IDLE",
            "energy": 0.0,
            "legacy_command": "idle",
            "confidence": "0.00",
        }

    energy = sum(float(v) for v in intent_vector) / len(intent_vector)

    if energy >= 0.65:
        command = "CONFIRM_INTENT"
        legacy = "accelerate"
    elif energy >= 0.40:
        command = "TRANSITION"
        legacy = "idle"
    else:
        command = "IDLE"
        legacy = "brake" if energy <= 0.3 else "idle"

    return {
        "command": command,
        "energy": round(energy, 4),
        "legacy_command": legacy,
        "confidence": f"{abs(energy):.2f}",
    }
