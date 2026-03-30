from typing import List

def fusion_vector(states: List[int], quantum_states: List[float]) -> List[float]:
    """
    Fusão simples para MVP:
    Combina os estados discretos com a matriz fluída do modelo simulado.
    """
    fused_results = []
    
    # Pad or zip depending on dimension match, just naive sum for MVP
    for state, q_state in zip((states * max(1, len(quantum_states))), quantum_states):
        fused_val = float(state) * 0.5 + q_state * 0.5
        fused_results.append(fused_val)
        
    return fused_results if fused_results else quantum_states
