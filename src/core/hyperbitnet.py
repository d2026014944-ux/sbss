"""
HyperBitnet — Rede topológica de estados ternários com fusão matricial.

Implementação original completa: grafo ponderado com propagação de estados
quânticos simulados via softmax, usando a base 1.58 (constante ternária do
BitNet 1.58b) como escalar de ativação nas matrizes e nos limiares de
atualização de nó.
"""

import random
from typing import Dict, List, Optional

import numpy as np
import networkx as nx
from scipy.special import softmax


# ---------------------------------------------------------------------------
# Matriz eficiente base-1.58
# ---------------------------------------------------------------------------

def bitnet_efficient_matrix(size: int, base: float = 1.58) -> np.ndarray:
    """
    Gera uma matriz (size × size) cujos elementos são  base^(i*size + j).
    Funciona como kernel de peso ternário escalonado para a rede.
    """
    return np.fromfunction(
        lambda i, j: base ** (i * size + j),
        (size, size),
        dtype=np.float64,
    )


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------

class HyperBitnet:
    """
    Rede neural-topológica inspirada em BitNet com propagação de estados
    quânticos rudimentares sobre um grafo ponderado.

    Cada nó possui:
      • state   – valor binário clássico (0 | 1)
      • q_state – valor contínuo ∈ [0, 1) representando a amplitude
                  de "probabilidade quântica" do nó.

    As arestas carregam peso (quantum_strength) que modula a influência
    entre vizinhos durante a atualização.
    """

    def __init__(self, num_nodes: int) -> None:
        self.graph: nx.Graph = nx.Graph()
        self.graph.add_nodes_from(range(num_nodes))
        self.states: Dict[int, int] = {
            node: random.choice([0, 1]) for node in self.graph.nodes()
        }
        self.quantum_states: Dict[int, float] = {
            node: np.random.random() for node in self.graph.nodes()
        }

    # ------------------------------------------------------------------
    # Construção do grafo
    # ------------------------------------------------------------------

    def connect_quantum_nodes(self, num_edges: int) -> None:
        """
        Cria *num_edges* arestas aleatórias com pesos quânticos ∈ (0, 1).
        """
        for _ in range(num_edges):
            node1, node2 = random.sample(list(self.graph.nodes()), 2)
            quantum_strength = np.random.random()
            self.graph.add_edge(node1, node2, weight=quantum_strength)

    # ------------------------------------------------------------------
    # Dinâmica de atualização
    # ------------------------------------------------------------------

    def update_node_state(self, node: int) -> None:
        """
        Atualiza o estado clássico e quântico de *node* com base nos
        vizinhos ponderados.

        • O limiar de ativação usa a constante 1.58 (BitNet ternário).
        • O estado quântico é atualizado via softmax sobre os q_states
          dos vizinhos.
        """
        neighbors = list(self.graph.neighbors(node))
        if not neighbors:
            return

        neighbor_states = [
            self.states[n] * self.graph[node][n]["weight"]
            for n in neighbors
        ]
        self.states[node] = int(sum(neighbor_states) > len(neighbors) / 1.58)

        self.quantum_states[node] = softmax(
            [self.quantum_states[n] for n in neighbors]
        )[0]

    # ------------------------------------------------------------------
    # Simulação
    # ------------------------------------------------------------------

    def run_quantum_simulation(self, num_steps: int) -> None:
        """
        Executa *num_steps* iterações completas de atualização sobre
        todos os nós do grafo.
        """
        for _ in range(num_steps):
            for node in self.graph.nodes():
                self.update_node_state(node)

    # ------------------------------------------------------------------
    # Helpers para integração com o pipeline
    # ------------------------------------------------------------------

    def get_state_vector(self) -> np.ndarray:
        """Retorna o vetor de estados clássicos como array NumPy."""
        return np.array([self.states[n] for n in sorted(self.graph.nodes())])

    def get_quantum_vector(self) -> np.ndarray:
        """Retorna o vetor de estados quânticos como array NumPy."""
        return np.array([self.quantum_states[n] for n in sorted(self.graph.nodes())])


# ---------------------------------------------------------------------------
# Fusão matricial HyperBitnet × BitNet
# ---------------------------------------------------------------------------

def hyperbitnet_matrix_fusion(
    hyperbitnet: HyperBitnet,
    bit_matrix: np.ndarray,
) -> np.ndarray:
    """
    Funde a topologia do HyperBitnet com uma matriz BitNet eficiente.

    Para cada par (i, j) conectado no grafo, o elemento da matriz de
    fusão é o produto:
        bit_matrix[i,j] × state_i × state_j × q_state_i × q_state_j

    Pares sem aresta recebem 0.
    """
    node_count = len(hyperbitnet.graph.nodes())
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
