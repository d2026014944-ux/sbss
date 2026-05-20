"""
brain-ia-bridge — Pipeline principal unificado.

Fluxo completo:
  1. Calibração adaptativa com detecção automática de domínio.
  2. Inferência ao vivo (Neurosity focus/calm/gamma).
  3. Simulação avançada HyperBitnet com fusão matricial (se deps disponíveis).
  4. Tradução para comando TRIBE.
"""

from __future__ import annotations

import sys

from core.calibration import calibrate_thresholds, state_from_score
from core.eeg_adapter import compute_score
from core.fusion import fusion_vector
from core.hyperbitnet import HyperBitnet
from integration.tribe_adapter import to_tribe_command

# Advanced mode check
try:
    import numpy as np
    from core.fusion import full_fusion
    from core.hyperbitnet import bitnet_efficient_matrix

    _HAS_ADVANCED = True
except ImportError:
    _HAS_ADVANCED = False


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NUM_NODES = 8
NUM_EDGES = 12
SIM_STEPS = 5


def collect_baseline_windows():
    """Simulate 30 resting-state windows for calibration."""
    return [
        {"focus": 0.30, "gamma": 0.28, "calm": 0.62},
        {"focus": 0.35, "gamma": 0.32, "calm": 0.60},
        {"focus": 0.33, "gamma": 0.30, "calm": 0.58},
        {"focus": 0.29, "gamma": 0.27, "calm": 0.65},
        {"focus": 0.31, "gamma": 0.29, "calm": 0.61},
        {"focus": 0.34, "gamma": 0.31, "calm": 0.59},
        {"focus": 0.32, "gamma": 0.30, "calm": 0.60},
        {"focus": 0.28, "gamma": 0.26, "calm": 0.66},
        {"focus": 0.36, "gamma": 0.33, "calm": 0.57},
        {"focus": 0.30, "gamma": 0.29, "calm": 0.63},
    ] * 3  # 30 windows


def run_mvp_demo():
    """MVP demo: calibration + live inference + TRIBE translation."""
    # 1) Initial calibration
    baseline = collect_baseline_windows()
    th = calibrate_thresholds(baseline)

    print("=== Calibration ===")
    print(
        {
            "baseline_mean": round(th.baseline_mean, 4),
            "baseline_std": round(th.baseline_std, 4),
            "low": round(th.low, 4),
            "high": round(th.high, 4),
        }
    )

    # 2) Sample real-time inference
    live_samples = [
        {"focus": 0.40, "gamma": 0.35, "calm": 0.50},  # likely transition
        {"focus": 0.82, "gamma": 0.78, "calm": 0.20},  # likely confirmed intent
        {"focus": 0.22, "gamma": 0.18, "calm": 0.70},  # likely disconnection
    ]

    print("\n=== Live Inference ===")
    for i, sample in enumerate(live_samples, start=1):
        score = compute_score(sample)
        state = state_from_score(score, th.low, th.high)

        net = HyperBitnet(n_nodes=NUM_NODES)
        net.inject_state(state)
        intent = fusion_vector(net.states, net.quantum_states)
        command = to_tribe_command(intent)

        print(
            f"sample_{i}:",
            {
                "score": round(score, 4),
                "state": state,
                "intent_energy": round(sum(intent), 4),
                "command": command["command"],
            },
        )

    return th


def run_advanced_simulation():
    """Advanced HyperBitnet simulation with quantum graph and matrix fusion."""
    if not _HAS_ADVANCED:
        print(
            "\n[Modo avançado indisponível — instale numpy, networkx, scipy]",
            file=sys.stderr,
        )
        return

    print("\n=== Advanced HyperBitnet Simulation ===")

    # 1) Build quantum graph
    print(f"\n[1] Inicializando HyperBitnet ({NUM_NODES} nós, {NUM_EDGES} arestas)...")
    hbn = HyperBitnet(num_nodes=NUM_NODES)
    hbn.connect_quantum_nodes(num_edges=NUM_EDGES)

    print(f"    -> Arestas efetivas: {hbn.graph.number_of_edges()}")
    print(f"    -> Estados iniciais:  {hbn.get_state_vector()}")
    print(f"    -> Q-states iniciais: {np.round(hbn.get_quantum_vector(), 3)}")

    # 2) Quantum simulation
    print(f"\n[2] Executando simulação quântica ({SIM_STEPS} passos)...")
    hbn.run_quantum_simulation(num_steps=SIM_STEPS)

    print(f"    -> Estados pós-sim:  {hbn.get_state_vector()}")
    print(f"    -> Q-states pós-sim: {np.round(hbn.get_quantum_vector(), 3)}")

    # 3) Matrix fusion
    print("\n[3] Fusão Matricial BitNet x HyperBitnet...")
    fusion_matrix = full_fusion(hbn)

    nonzero = int(np.count_nonzero(fusion_matrix))
    energy = float(np.sum(fusion_matrix))
    print(f"    -> Dimensão:      {fusion_matrix.shape}")
    print(f"    -> Elementos != 0: {nonzero}")
    print(f"    -> Energia total:  {energy:.6f}")

    # 4) TRIBE command from fused vector
    fused = fusion_vector(hbn.states, hbn.quantum_states)
    tribe_cmd = to_tribe_command(fused)
    print(f"\n[4] Comando TRIBE: {tribe_cmd}")

    print("\n✓ Simulação avançada completa.")


def main():
    run_mvp_demo()
    run_advanced_simulation()


if __name__ == "__main__":
    main()
