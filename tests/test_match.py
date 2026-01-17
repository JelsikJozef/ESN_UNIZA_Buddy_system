"""Confirm the unweighted Hamming distance ignores invalid answers."""

import numpy as np

from src.model import match


def test_hamming_distance_handles_invalid_answers():
    esn = np.array([[0, 1, np.nan]])
    erasmus = np.array([[0, 0, 1]])

    dist = match.compute_distance_matrix(esn, erasmus)

    # Third question ignored due to nan, so distance is 1 (only position 2 differs)
    assert dist.shape == (1, 1)
    assert dist[0, 0] == 1.0
