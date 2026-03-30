from typing import List, Dict

def to_tribe_command(intent_vector: List[float]) -> Dict[str, str]:
    """
    Traduz vetor de intenção em comando simbólico de alto nível.
    """
    if not intent_vector:
        return {"command": "idle", "confidence": "0.0"}
        
    avg_intent = sum(intent_vector) / len(intent_vector)
    
    if avg_intent >= 0.6:
        cmd = "accelerate"
    elif avg_intent <= 0.3:
        cmd = "brake"
    else:
        cmd = "idle"
        
    return {
        "command": cmd,
        "confidence": f"{abs(avg_intent):.2f}"
    }
