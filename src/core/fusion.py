"""
Fusion Engine — Agrega saídas do pipeline EEG + HyperBitnet.

Duas camadas de fusão:
  1. fusion_vector()   — fusão leve (vetor) para loop realtime.
  2. full_fusion()     — fusão matricial completa via hyperbitnet_matrix_fusion.
"""

from __future__ import annotations

from typing import List

from core.hyperbitnet import HyperBitnet

# Advanced mode check
try:
    import numpy as np

    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


def fusion_vector(
    states: List[float],
    quantum_states: List[float],
) -> List[float]:
    """
    Fuse classical and quantum-inspired node states into a single intent vector.

    Each output element is the arithmetic mean of the corresponding classical
    and quantum state, keeping values in [0, 1].
    """
    if not states and not quantum_states:
        return []
    return [(float(s) + float(q)) / 2.0 for s, q in zip(states, quantum_states)]


def full_fusion(hbn: HyperBitnet):
    """
    Full matrix fusion using BitNet 1.58b efficient matrix.

    Generates the BitNet Efficient Matrix sized to the graph's nodes
    and applies hyperbitnet_matrix_fusion for the final result matrix.

    Requires numpy/networkx/scipy.
    """
    if not _HAS_NUMPY:
        raise RuntimeError("full_fusion requires numpy/networkx/scipy")

    from core.hyperbitnet import bitnet_efficient_matrix, hyperbitnet_matrix_fusion

    num_nodes = hbn.n_nodes
    bit_matrix = bitnet_efficient_matrix(num_nodes)
    return hyperbitnet_matrix_fusion(hbn, bit_matrix)
