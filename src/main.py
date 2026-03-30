from core.eeg_adapter import compute_score
from core.calibration import calibrate_thresholds, state_from_score
from core.hyperbitnet import HyperBitnet
from core.fusion import fusion_vector
from integration.tribe_adapter import to_tribe_command
import random

def mock_eeg_stream():
    for _ in range(30):
        yield {"alpha": random.uniform(0.1, 0.9), "beta": random.uniform(0.1, 0.9)}

def main():
    print("[1] Iniciando baseline para calibração de Threshold (30 janelas)...")
    baseline = []
    for metrics in mock_eeg_stream():
        baseline.append(compute_score(metrics))
        
    calib_result = calibrate_thresholds(baseline)
    print(f"-> Limites definidos: Low={calib_result.thresholds.low:.2f}, High={calib_result.thresholds.high:.2f}")

    print("\n[2] Inicializando HyperBitnet e Processando...")
    hbn = HyperBitnet()
    
    # Simula pacote isolado realtime
    metrics = {"alpha": 0.85, "beta": 0.20}
    score = compute_score(metrics)
    state = state_from_score(score, calib_result.thresholds)
    
    q_state = hbn.process(state)
    fused = fusion_vector([state], q_state)
    
    tribe_cmd = to_tribe_command(fused)
    
    print(f"-> Estado Bruto: {state}")
    print(f"-> Vetor Fundido (Fusão): {fused}")
    print(f"-> Comando Analisado para TRIBE: {tribe_cmd}")

if __name__ == "__main__":
    main()
