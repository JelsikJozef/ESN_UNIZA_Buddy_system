from typing import Tuple

import numpy as np


def _hamming_distance(esn_vector: np.ndarray, erasmus_vector: np.ndarray) -> float:
    valid_mask = ~np.isnan(esn_vector) & ~np.isnan(erasmus_vector)
    if not valid_mask.any():
        return 0.0
    return float(np.sum(esn_vector[valid_mask] != erasmus_vector[valid_mask]))


def compute_distance_matrix(esn_vectors: np.ndarray, erasmus_vectors: np.ndarray) -> np.ndarray:
    esn_count, erasmus_count = esn_vectors.shape[0], erasmus_vectors.shape[0]
    distances = np.empty((esn_count, erasmus_count), dtype=float)
    for i in range(esn_count):
        for j in range(erasmus_count):
            distances[i, j] = _hamming_distance(esn_vectors[i], erasmus_vectors[j])
    return distances
