"""
HyperBitnet — Rede topológica de estados ternários com fusão matricial.

Modo base (pure-Python):
  Suporta inject_state(), states e quantum_states como listas simples.
  Zero dependências externas.

Modo avançado (numpy/networkx/scipy):
  Grafo ponderado com propagação quântica simulada via softmax,
  usando a base 1.58 (constante ternária do BitNet 1.58b) como
  escalar de ativação. Fusão matricial HyperBitnet × BitNet.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Graceful degradation: mesma filosofia do _native_loader.py
# ---------------------------------------------------------------------------

try:
    import numpy as np
    import networkx as nx
    from scipy.special import softmax

    _HAS_ADVANCED = True
except ImportError:
    _HAS_ADVANCED = False


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------


class HyperBitnet:
    """
    Hybrid HyperBitnet supporting both lightweight and advanced modes.

    Lightweight (pure Python):
      - inject_state(intent_state) for pipeline integration
      - states / quantum_states as plain lists

    Advanced (requires numpy/networkx/scipy):
      - Graph-based topology with weighted quantum edges
      - run_quantum_simulation() for state propagation
      - BitNet 1.58b matrix fusion
    """

    def __init__(
        self,
        n_nodes: int = 8,
        num_nodes: int | None = None,
        seed: int | None = None,
    ) -> None:
        # Accept both parameter names
        self.n_nodes = num_nodes if num_nodes is not None else n_nodes
        self._rng = random.Random(seed)

        # Core state vectors (always available, plain lists)
        self.states: List[float] = [0.0] * self.n_nodes
        self.quantum_states: List[float] = [0.5] * self.n_nodes

        # Advanced mode: initialize graph if deps available
        self._graph: Optional[object] = None
        if _HAS_ADVANCED:
            self._init_advanced()

    # ------------------------------------------------------------------
    # Advanced mode initialization
    # ------------------------------------------------------------------

    def _init_advanced(self) -> None:
        """Initialize networkx graph for advanced operations."""
        self._graph = nx.Graph()
        self._graph.add_nodes_from(range(self.n_nodes))
        for node in self._graph.nodes():
            self._graph.nodes[node]["state"] = self.states[node]
            self._graph.nodes[node]["q_state"] = self.quantum_states[node]

    # ------------------------------------------------------------------
    # Core API (always available, pure Python)
    # ------------------------------------------------------------------

    def inject_state(self, intent_state: int) -> None:
        """
        Propagate a discrete intent state (-1, 0, 1) into all nodes.

        intent_state mapping:
          -1 -> 0.0  (idle / disconnected)
           0 -> 0.5  (ambiguous)
           1 -> 1.0  (confirmed intent)
        """
        bias = (intent_state + 1) / 2.0
        for i in range(self.n_nodes):
            noise = self._rng.gauss(0.0, 0.05)
            classical = max(0.0, min(1.0, bias + noise))
            self.states[i] = classical
            # Quantum projection: cosine mapping for superposition coherence
            angle = math.pi * (1.0 - classical)
            self.quantum_states[i] = (1.0 + math.cos(angle)) / 2.0

        # Sync to graph if in advanced mode
        if self._graph is not None:
            self._sync_to_graph()

    # ------------------------------------------------------------------
    # Advanced API (requires numpy/networkx/scipy)
    # ------------------------------------------------------------------

    @property
    def graph(self):
        """Access the networkx graph (advanced mode only)."""
        if self._graph is None:
            if not _HAS_ADVANCED:
                raise RuntimeError(
                    "Advanced graph operations require numpy, networkx, and scipy. "
                    "Install them with: pip install numpy networkx scipy"
                )
            self._init_advanced()
        return self._graph

    def connect_quantum_nodes(self, num_edges: int) -> None:
        """Create random weighted quantum edges on the graph."""
        if not _HAS_ADVANCED:
            raise RuntimeError("connect_quantum_nodes requires numpy/networkx")
        for _ in range(num_edges):
            node1, node2 = random.sample(list(self.graph.nodes()), 2)
            quantum_strength = np.random.random()
            self.graph.add_edge(node1, node2, weight=quantum_strength)

    def update_node_state(self, node: int) -> None:
        """
        Update classical and quantum state of a node based on neighbors.

        Uses the 1.58 constant (BitNet ternary) as activation threshold
        and softmax over neighbor quantum states.
        """
        if not _HAS_ADVANCED:
            raise RuntimeError("update_node_state requires numpy/networkx/scipy")
        neighbors = list(self.graph.neighbors(node))
        if not neighbors:
            return

        neighbor_states = [
            self.states[n] * self.graph[node][n]["weight"] for n in neighbors
        ]
        self.states[node] = float(int(sum(neighbor_states) > len(neighbors) / 1.58))
        self.quantum_states[node] = float(
            softmax([self.quantum_states[n] for n in neighbors])[0]
        )
        self._sync_to_graph()

    def run_quantum_simulation(self, num_steps: int) -> None:
        """Run full graph state propagation for num_steps iterations."""
        if not _HAS_ADVANCED:
            raise RuntimeError("run_quantum_simulation requires numpy/networkx/scipy")
        for _ in range(num_steps):
            for node in self.graph.nodes():
                self.update_node_state(node)

    def get_state_vector(self):
        """Return classical states as numpy array (or list in base mode)."""
        if _HAS_ADVANCED:
            return np.array(self.states)
        return self.states[:]

    def get_quantum_vector(self):
        """Return quantum states as numpy array (or list in base mode)."""
        if _HAS_ADVANCED:
            return np.array(self.quantum_states)
        return self.quantum_states[:]

    # ------------------------------------------------------------------
    # Internal sync
    # ------------------------------------------------------------------

    def _sync_to_graph(self) -> None:
        """Keep graph node attributes in sync with list states."""
        if self._graph is None:
            return
        for node in self._graph.nodes():
            self._graph.nodes[node]["state"] = self.states[node]
            self._graph.nodes[node]["q_state"] = self.quantum_states[node]


# ---------------------------------------------------------------------------
# Advanced matrix operations (require numpy)
# ---------------------------------------------------------------------------


def bitnet_efficient_matrix(size: int, base: float = 1.58):
    """
    Generate a BitNet 1.58b efficient weight matrix.

    Each element is base^(i*size + j), forming a ternary-scaled kernel.
    """
    if not _HAS_ADVANCED:
        raise RuntimeError("bitnet_efficient_matrix requires numpy")
    return np.fromfunction(
        lambda i, j: base ** (i * size + j),
        (size, size),
        dtype=np.float64,
    )


def hyperbitnet_matrix_fusion(
    hyperbitnet: HyperBitnet,
    bit_matrix,
):
    """
    Fuse HyperBitnet topology with a BitNet efficient matrix.

    For each connected pair (i, j):
      fusion[i,j] = bit_matrix[i,j] × state_i × state_j × q_state_i × q_state_j

    Disconnected pairs receive 0.
    """
    if not _HAS_ADVANCED:
        raise RuntimeError("hyperbitnet_matrix_fusion requires numpy/networkx")

    node_count = hyperbitnet.n_nodes
    matrix_size = bit_matrix.shape[0]

    if node_count != matrix_size:
        raise ValueError(
            f"HyperBitnet nodes ({node_count}) and matrix size "
            f"({matrix_size}) must match."
        )

    fusion_result = np.zeros((node_count, node_count), dtype=np.float64)

    for i in range(node_count):
        for j in range(node_count):
            if hyperbitnet.graph.has_edge(i, j):
                fusion_result[i, j] = (
                    bit_matrix[i, j]
                    * hyperbitnet.states[i]
                    * hyperbitnet.states[j]
                    * hyperbitnet.quantum_states[i]
                    * hyperbitnet.quantum_states[j]
                )

    return fusion_result
