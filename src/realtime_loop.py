import time
from collections import deque, Counter
from typing import Dict, Iterable, List
import random

from core.eeg_adapter import compute_score
from core.calibration import calibrate_thresholds, state_from_score

def realtime_loop_run(duration_seconds: int = 15):
    print("Iniciando buffer deslizante (1-2s) focado em evitar falso-positivo...")
    buffer = deque(maxlen=5) # janela de tempo local
    
    # Limites estáticos como calibração mock rápida para rodar
    thresholds = calibrate_thresholds([0.5, 0.4, 0.6]).thresholds
    
    start_time = time.time()
    loops = 0
    while time.time() - start_time < duration_seconds:
        # Mocking input do headset
        metrics = {"alpha": random.uniform(0.0, 1.0), "beta": random.uniform(0.2, 0.8)}
        score = compute_score(metrics)
        state = state_from_score(score, thresholds)
        
        buffer.append(state)
        
        if len(buffer) == buffer.maxlen:
            # Suavização por maioria
            most_common = Counter(buffer).most_common(1)[0][0]
            print(f"Tempo {loops*0.5:.1f}s | Real: {state:>2} | Maioria Filtrada (Buffer): {most_common:>2}")
            
        time.sleep(0.5)
        loops += 1

if __name__ == "__main__":
    realtime_loop_run(10)
