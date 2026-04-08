"""
Fusion Engine — Agrega saídas do pipeline EEG + HyperBitnet.

Duas camadas de fusão:
  1. fusion_vector()   — fusão leve (vetor) para loop realtime.
  2. full_fusion()     — fusão matricial completa via hyperbitnet_matrix_fusion.
"""

from typing import List

import numpy as np

from .hyperbitnet import (
    HyperBitnet,
    bitnet_efficient_matrix,
    hyperbitnet_matrix_fusion,
)


def fusion_vector(
    classical_states: List[int],
    quantum_states: List[float],
) -> List[float]:
    """
    Fusão leve para uso no loop de tempo-real.

    Combina estados clássicos (discretos) com estados quânticos (contínuos)
    usando média ponderada 50/50. Retorna lista de floats prontos para o
    tribe_adapter.
    """
    fused: List[float] = []
    for state, q_state in zip(classical_states, quantum_states):
        fused.append(float(state) * 0.5 + q_state * 0.5)
    return fused if fused else list(quantum_states)


def full_fusion(hbn: HyperBitnet) -> np.ndarray:
    """
    Fusão matricial completa.

    Gera a BitNet Efficient Matrix com tamanho correspondente aos nós
    do grafo e aplica hyperbitnet_matrix_fusion para produzir a matriz
    de resultado final.
    """
    num_nodes = len(hbn.graph.nodes())
    bit_matrix = bitnet_efficient_matrix(num_nodes)
    return hyperbitnet_matrix_fusion(hbn, bit_matrix)
